# PortAudio on PC
此專案使用PortAudio實現 WinPC 端即時訊號處理，分別使用 PortAudio API 實現 C語言 以及 PyAudio 實現 Python 。

## usage

---
透過USB麥克風將輸入訊號傳入PC後，透過 PortAudio 擷取訊號並進行演算法計算
![portaudio process](https://user-images.githubusercontent.com/48181705/153815539-b62740e3-64e8-4f65-921f-12bf8e421160.png)


## Reference

---
> [PortAudio API](http://www.portaudio.com/)    
> [PortAudio 2.0](http://portaudio.com/docs/v19-doxydocs/compile_windows_mingw.html)    
> [PyAudio](http://people.csail.mit.edu/hubert/pyaudio/)    
> [Unofficial Windows Binaries for Python Extension Packages](https://www.lfd.uci.edu/~gohlke/pythonlibs/) : 在這可以找到 PyAudio 的擴展包
