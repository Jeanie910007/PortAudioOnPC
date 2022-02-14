# PortAudio 使用說明

## Port Audio API 介紹

----
為免費跨平台的輸入輸出API程式庫
* Windows 支援 MME,DirectSound, WASAPI, ASIO，
* Linux 支援 ALSA
    
> [PortAudio 官方網站](http://portaudio.com/docs/v19-doxydocs/tutorial_start.html)

## PortAudio API with CMake

----
* 將 Lib 中的 ```libportaudio-2.dll``` 以及 ```libsndfile-1.dll``` 放入 mingw64 中的 bin 資料夾內 (ex: C:\msys64\mingw64\bin)
* CMakeLists.txt 內容不需更動

## PortAudio API 主要 API 指令

----
* Pa_Initialize : API 初始化
* Pa_GetDefaultInputDevice : 取得預設輸入裝置
* Pa_GetDefaultOutputDevice : 取得預設輸出裝置
* Pa_OpenStream : 開啟訊號流、錄放音設備
* processCallback : 回調函數
* Pa_StartStream : 開始訊號流傳輸
* Pa_IsStreamActive : 確認訊號是持續運行
* Pa_Sleep : 主程式不進行任何動作，只進行回調
* Pa_StopStream : 暫停訊號流傳輸
* Pa_CloseStream : 關閉訊號流
* Pa_Terminate : 終止API

## PortAudio 使用注意事項
* 若需要新增演算法，將演算法程式放入 src 資料夾中，並在 CMakeLists 中 ```add_executable```
* 程式需使用 overlap 以免 frame 間產生不連續感