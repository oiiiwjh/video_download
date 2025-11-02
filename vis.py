# -----------------------------------------------------------------------------
# Copyright (c) 2025, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
# -----------------------------------------------------------------------------

import argparse
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
import pickle as pkl
import plotly.graph_objs as go
import plotly.io as pio
from tqdm import tqdm

matplotlib.use("agg")


class Pose():
    """
    A class of operations on camera poses (numpy arrays with shape [...,3,4]).
    Each [3,4] camera pose takes the form of [R|t].
    """

    def __call__(self, R=None, t=None):
        """
        Construct a camera pose from the given rotation matrix R and/or translation vector t.

        Args:
            R: Rotation matrix [...,3,3] or None
            t: Translation vector [...,3] or None

        Returns:
            pose: Camera pose matrix [...,3,4]
        """
        assert R is not None or t is not None
        if R is None:
            if not isinstance(t, np.ndarray):
                t = np.array(t)
            R = np.eye(3, device=t.device).repeat(*t.shape[:-1], 1, 1)
        elif t is None:
            if not isinstance(R, np.ndarray):
                R = np.array(R)
            t = np.zeros(R.shape[:-1], device=R.device)
        else:
            if not isinstance(R, np.ndarray):
                R = np.array(R)
            if not isinstance(t, np.ndarray):
                t = np.tensor(t)
        assert R.shape[:-1] == t.shape and R.shape[-2:] == (3, 3)
        R = R.astype(np.float32)
        t = t.astype(np.float32)
        pose = np.concatenate([R, t[..., None]], axis=-1)  # [...,3,4]
        assert pose.shape[-2:] == (3, 4)
        return pose

    def invert(self, pose, use_inverse=False):
        """
        Invert a camera pose.

        Args:
            pose: Camera pose matrix [...,3,4]
            use_inverse: Whether to use matrix inverse instead of transpose

        Returns:
            pose_inv: Inverted camera pose matrix [...,3,4]
        """
        R, t = pose[..., :3], pose[..., 3:]
        R_inv = R.inverse() if use_inverse else R.transpose(0, 2, 1)
        t_inv = (-R_inv @ t)[..., 0]
        pose_inv = self(R=R_inv, t=t_inv)
        return pose_inv

    def compose(self, pose_list):
        """
        Compose a sequence of poses together.
        pose_new(x) = poseN o ... o pose2 o pose1(x)

        Args:
            pose_list: List of camera poses to compose

        Returns:
            pose_new: Composed camera pose
        """
        pose_new = pose_list[0]
        for pose in pose_list[1:]:
            pose_new = self.compose_pair(pose_new, pose)
        return pose_new

    def compose_pair(self, pose_a, pose_b):
        """
        Compose two poses together.
        pose_new(x) = pose_b o pose_a(x)

        Args:
            pose_a: First camera pose
            pose_b: Second camera pose

        Returns:
            pose_new: Composed camera pose
        """
        R_a, t_a = pose_a[..., :3], pose_a[..., 3:]
        R_b, t_b = pose_b[..., :3], pose_b[..., 3:]
        R_new = R_b @ R_a
        t_new = (R_b @ t_a + t_b)[..., 0]
        pose_new = self(R=R_new, t=t_new)
        return pose_new

    def scale_center(self, pose, scale):
        """
        Scale the camera center from the origin.
        0 = R@c+t --> c = -R^T@t (camera center in world coordinates)
        0 = R@(sc)+t' --> t' = -R@(sc) = -R@(-R^T@st) = st

        Args:
            pose: Camera pose to scale
            scale: Scale factor

        Returns:
            pose_new: Scaled camera pose
        """
        R, t = pose[..., :3], pose[..., 3:]
        pose_new = np.concatenate([R, t * scale], axis=-1)
        return pose_new


def to_hom(X):
    """Get homogeneous coordinates of the input by appending ones."""
    X_hom = np.concatenate([X, np.ones_like(X[..., :1])], axis=-1)
    return X_hom


def cam2world(X, pose):
    """Transform points from camera to world coordinates."""
    X_hom = to_hom(X)
    pose_inv = Pose().invert(pose)
    return X_hom @ pose_inv.transpose(0, 2, 1)


def get_camera_mesh(pose, depth=1):
    """
    Create a camera mesh visualization.

    Args:
        pose: Camera pose matrix
        depth: Size of the camera frustum

    Returns:
        vertices: Camera mesh vertices
        faces: Camera mesh faces
        wireframe: Camera wireframe vertices
    """
    vertices = np.array([[-0.5, -0.5, 1],
                         [0.5, -0.5, 1],
                         [0.5, 0.5, 1],
                         [-0.5, 0.5, 1],
                         [0, 0, 0]]) * depth  # [6,3]
    faces = np.array([[0, 1, 2],
                      [0, 2, 3],
                      [0, 1, 4],
                      [1, 2, 4],
                      [2, 3, 4],
                      [3, 0, 4]])  # [6,3]
    vertices = cam2world(vertices[None], pose)  # [N,6,3]
    wireframe = vertices[:, [0, 1, 2, 3, 0, 4, 1, 2, 4, 3]]  # [N,10,3]
    return vertices, faces, wireframe


def merge_xyz_indicators_plotly(xyz):
    """Merge xyz coordinate indicators for plotly visualization."""
    xyz = xyz[:, [[-1, 0], [-1, 1], [-1, 2]]]  # [N,3,2,3]
    xyz_0, xyz_1 = unbind_np(xyz, axis=2)  # [N,3,3]
    xyz_dummy = xyz_0 * np.nan
    xyz_merged = np.stack([xyz_0, xyz_1, xyz_dummy], axis=2)  # [N,3,3,3]
    xyz_merged = xyz_merged.reshape(-1, 3)
    return xyz_merged


def get_xyz_indicators(pose, length=0.1):
    """Get xyz coordinate axis indicators for a camera pose."""
    xyz = np.eye(4, 3)[None] * length
    xyz = cam2world(xyz, pose)
    return xyz


def merge_wireframes_plotly(wireframe):
    """Merge camera wireframes for plotly visualization."""
    wf_dummy = wireframe[:, :1] * np.nan
    wireframe_merged = np.concatenate([wireframe, wf_dummy], axis=1).reshape(-1, 3)
    return wireframe_merged


def merge_meshes(vertices, faces):
    """Merge multiple camera meshes into a single mesh."""
    mesh_N, vertex_N = vertices.shape[:2]
    faces_merged = np.concatenate([faces + i * vertex_N for i in range(mesh_N)], axis=0)
    vertices_merged = vertices.reshape(-1, vertices.shape[-1])
    return vertices_merged, faces_merged


def unbind_np(array, axis=0):
    """Split numpy array along specified axis into list."""
    if axis == 0:
        return [array[i, :] for i in range(array.shape[0])]
    elif axis == 1 or (len(array.shape) == 2 and axis == -1):
        return [array[:, j] for j in range(array.shape[1])]
    elif axis == 2 or (len(array.shape) == 3 and axis == -1):
        return [array[:, :, j] for j in range(array.shape[2])]
    else:
        raise ValueError("Invalid axis. Use 0 for rows or 1 for columns.")


def plotly_visualize_pose(poses, vis_depth=0.5, xyz_length=0.5, center_size=2, xyz_width=5, mesh_opacity=0.05):
    """
    Create plotly visualization traces for camera poses.

    Args:
        poses: Camera poses to visualize [N,3,4]
        vis_depth: Size of camera frustum visualization
        xyz_length: Length of coordinate axis indicators
        center_size: Size of camera center markers
        xyz_width: Width of coordinate axis lines
        mesh_opacity: Opacity of camera frustum mesh

    Returns:
        plotly_traces: List of plotly visualization traces
    """
    N = len(poses)
    centers_cam = np.zeros([N, 1, 3])
    centers_world = cam2world(centers_cam, poses)
    centers_world = centers_world[:, 0]
    # Get the camera wireframes.
    vertices, faces, wireframe = get_camera_mesh(poses, depth=vis_depth)
    xyz = get_xyz_indicators(poses, length=xyz_length)
    vertices_merged, faces_merged = merge_meshes(vertices, faces)
    wireframe_merged = merge_wireframes_plotly(wireframe)
    xyz_merged = merge_xyz_indicators_plotly(xyz)
    # Break up (x,y,z) coordinates.
    wireframe_x, wireframe_y, wireframe_z = unbind_np(wireframe_merged, axis=-1)
    xyz_x, xyz_y, xyz_z = unbind_np(xyz_merged, axis=-1)
    centers_x, centers_y, centers_z = unbind_np(centers_world, axis=-1)
    vertices_x, vertices_y, vertices_z = unbind_np(vertices_merged, axis=-1)
    # Set the color map for the camera trajectory and the xyz indicators.
    color_map = plt.get_cmap("gist_rainbow")  # red -> yellow -> green -> blue -> purple
    center_color = []
    faces_merged_color = []
    wireframe_color = []
    xyz_color = []
    x_color, y_color, z_color = *np.eye(3).T,
    for i in range(N):
        # Set the camera pose colors (with a smooth gradient color map).
        r, g, b, _ = color_map(i / (N - 1))
        rgb = np.array([r, g, b]) * 0.8
        wireframe_color += [rgb] * 11
        center_color += [rgb]
        faces_merged_color += [rgb] * 6
        xyz_color += [x_color] * 3 + [y_color] * 3 + [z_color] * 3
    # Plot in plotly.
    plotly_traces = [
        go.Scatter3d(x=wireframe_x, y=wireframe_y, z=wireframe_z, mode="lines",
                     line=dict(color=wireframe_color, width=1)),
        go.Scatter3d(x=xyz_x, y=xyz_y, z=xyz_z, mode="lines", line=dict(color=xyz_color, width=xyz_width)),
        go.Scatter3d(x=centers_x, y=centers_y, z=centers_z, mode="markers",
                     marker=dict(color=center_color, size=center_size, opacity=1)),
        go.Mesh3d(x=vertices_x, y=vertices_y, z=vertices_z,
                  i=[f[0] for f in faces_merged], j=[f[1] for f in faces_merged], k=[f[2] for f in faces_merged],
                  facecolor=faces_merged_color, opacity=mesh_opacity),
    ]
    return plotly_traces


def write_html(poses, file, dset, vis_depth=1, xyz_length=0.2, center_size=0.01, xyz_width=2):
    """Write camera pose visualization to HTML file."""
    if dset == "lightspeed":
        xyz_length = xyz_length / 3
        xyz_width = xyz_width
        vis_depth = vis_depth / 3
        center_size *= 3
    traces_poses = plotly_visualize_pose(poses, vis_depth=vis_depth, xyz_length=xyz_length,
                                         center_size=center_size, xyz_width=xyz_width, mesh_opacity=0.05)
    traces_all2 = traces_poses
    layout2 = go.Layout(scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False),
                                   dragmode="orbit", aspectratio=dict(x=1, y=1, z=1), aspectmode="data"),
                        height=400, width=600, showlegend=False)

    fig2 = go.Figure(data=traces_all2, layout=layout2)
    html_str2 = pio.to_html(fig2, full_html=False)

    file.write(html_str2)


def viz_poses(i, seq, file, dset, dset_parent):
    """Visualize camera poses for a sequence and write to HTML file."""
    if "/" in seq:
        seq = "_".join(seq.split("/"))

    if "mp4" in seq:
        seq = seq[:-4]

    file.write(f"<span style='font-size: 18pt;'>{i} {seq}</span><br>")

    if dset == "dynpose_100k":
        with open(f"{dset_parent}/cameras/{seq}.pkl", "rb") as f:
            poses = pkl.load(f)["poses"]
    else:
        with open(f"{dset_parent}/poses.pkl", "rb") as f:
            poses = pkl.load(f)[seq]

    write_html(poses, file, dset)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dset", type=str, default="dynpose_100k", choices=["dynpose_100k", "lightspeed"])
    parser.add_argument("--dset_parent", type=str, default=".")
    args = parser.parse_args()

    outdir = f"pose_viz/{args.dset}"
    os.makedirs(outdir, exist_ok=True)
    split_size = 6  # to avoid poses disappearing

    viz_list = f"{args.dset_parent}/viz_list.txt"
    seqs = open(viz_list).read().split()

    for j in tqdm(range(int(np.ceil(len(seqs)/split_size)))):
        with open(f"{outdir}/index_{str(j)}.html", "w") as file:
            for i, seq in enumerate(tqdm(seqs[j*split_size:j*split_size+split_size])):
                viz_poses(i, seq, file, args.dset, args.dset_parent)