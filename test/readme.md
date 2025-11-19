https://www.youtube.com/watch?v=PySzLfnAeuE

ID      EXT   RESOLUTION FPS HDR CH │   FILESIZE    TBR PROTO │ VCODEC         VBR ACODEC      ABR ASR MORE INFO
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
136     mp4   1280x720    30        │    1.18GiB  2149k https │ avc1.64001f # 3.1 2149k video only          720p, mp4_dash
247     webm  1280x720    30        │    1.23GiB  2234k https │ vp9          2234k video only          720p, webm_dash
300     mp4   1280x720    60        │ ~  2.96GiB  5384k m3u8  │ avc1.640020 # 3.2       mp4a.40.2
298     mp4   1280x720    60        │    2.10GiB  3824k https │ avc1.640020  3824k video only          720p60, mp4_dash
302     webm  1280x720    60        │    2.02GiB  3671k https │ vp9          3671k video only          720p60, webm_dash
334     webm  1280x720    60 10     │    2.46GiB  4484k https │ vp9.2        4484k video only          720p60 HDR, webm_dash

301     mp4   1920x1080   60        │ ~  4.21GiB  7663k m3u8  │ avc1.64002A # 4.2       mp4a.40.2
299     mp4   1920x1080   60        │    3.32GiB  6038k https │ avc1.64002a  6038k video only          1080p60, mp4_dash
303     webm  1920x1080   60        │    3.49GiB  6357k https │ vp9          6357k video only          1080p60, webm_dash
335     webm  1920x1080   60 10     │    3.77GiB  6867k https │ vp9.2        6867k video only          1080p60 HDR, webm_dash
308     webm  2560x1440   60        │    8.21GiB 14950k https │ vp9         14950k video only          1440p60, webm_dash
336     webm  2560x1440   60 10     │    8.98GiB 16359k https │ vp9.2       16359k video only          1440p60 HDR, webm_dash
315     webm  3840x2160   60        │   16.46GiB 29979k https │ vp9         29979k video only          2160p60, webm_dash
337     webm  3840x2160   60 10     │   15.78GiB 28730k https │ vp9.2       28730k video only          2160p60 HDR, webm_dash


## yt-dlp 版本
➜ conda list | grep yt-dlp 
yt-dlp                    2025.10.14               pypi_0    pypi
pip install yt-dlp==2025.10.14      
## yt-dlp cookie get
https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies

## 下载示例
https://www.youtube.com/watch?v=PySzLfnAeuE
format: https://github.com/yt-dlp/yt-dlp?tab=readme-ov-file#filtering-formats
format 格式排序：https://github.com/yt-dlp/yt-dlp?tab=readme-ov-file#sorting-formats
output format：https://github.com/yt-dlp/yt-dlp?tab=readme-ov-file#output-template-examples
- 查看可用格式：
yt-dlp -F --list-formats  https://www.youtube.com/watch\?v\=PySzLfnAeuE --cookies cookie_1102.txt --geo-verification-proxy https://127.0.0.1:7897
- 下载指定格式，例如 299：
yt-dlp -f 299 https://www.youtube.com/watch\?v\=PySzLfnAeuE --cookies cookie_1102.txt --geo-verification-proxy https://127.0.0.1:7897
yt-dlp -f "all[height=720]" https://www.youtube.com/watch\?v\=PySzLfnAeuE --cookies cookie_1102.txt
<!-- -f "bv[height<=?720][tbr>500]" -->
<!-- -f "all[vcodec=none]" -->
yt-dlp -f "all" https://www.youtube.com/watch\?v\=4xA_0zaD6Rc --cookies cookie_1102.txt -o "%(id)s.%(ext)s"  
yt-dlp -f "all" https://www.youtube.com/watch\?v\=4xA_0zaD6Rc --cookies cookie_1102.txt -o "%(format)s_%(id)s_%{alt_title}s.%(ext)s"  
yt-dlp -f "all" https://www.youtube.com/watch\?v\=MxvLovySHP8 --cookies cookie_1102.txt -o "%(vcodec)s_%(format)s_%(id)s_%(alt_title)s_%(location)s_%(categories)s_%(tags)s_%(description)s.%(ext)s"