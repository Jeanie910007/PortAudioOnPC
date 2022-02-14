# pyaudio_algorithm 使用說明

## pyauido 軟體安裝注意事項

----
* 目前 pyaudio 只支援到 Python 3.6, 請使用 Anaconda 安裝3.6 環境
* 透過 資料夾內之 PyAudio-0.2.11-cp36-cp36m-win_amd64.whlPyAudio-0.2.11-cp36-cp36m-win_amd64.whl 檔案安裝 pyaudio，否則無法執行4ch訊號輸入

        pip install PyAudio-0.2.11-cp36-cp36m-win_amd64.whlPyAudio-0.2.11-cp36-cp36m-win_amd64.whl

## pyaudio_algorithm 程式架構

----
1. class MicrophoneStream

    此類別是麥克風訊號流 callback:
        
    *  ```_fill_buffer``` : 為pyaudio callback取值
    * ```generator``` : 將byte 訊號轉換成float
    *  ```save_audio``` : 將錄音後訊號轉成 wav檔

2. class thread_processed

    此類別是與多執行序相關的程式:
    * ```get_audio_loop```: 為不停呼叫 generator 進行輸入訊號解碼
    * ```play_processed_audio``` :為不斷將處理後訊號撥出
    * ```execute_acoustic_algorithm``` : 為主要演算法處理處，目前僅針對 ch1 進行 lowpass 並輸出。錄音模式輸出為2ch,ch1 : 原始錄音訊號, ch2 : 處理後訊號。撥放模式輸出為2ch, ch1 & ch2 : 處理後訊號。

3. class signal_algorithm

    此類別是訊號處理相關演算法:
    * ```low_pass_process``` : 頻域低通濾波器，輸入目前音訊以及截止頻率即可進行濾波。


## pyaudio_algorithm 注意事項

----
* 首次使用時，需確認聲音裝置名稱，可將第 197 行 ```print(device_list)``` 註解關閉，了解目前電腦所連接到的裝置名稱為何以及內部資訊是否正確。輸出裝置請於第 202 行之 output_device_index 進行修改。輸入裝置則需要從 "系統" $\rightarrow$ "聲音" $\rightarrow$ "錄製" 中確認預設裝置為你要的即可。
* 參數修改 :

    1. ```RUN_MODE``` : 
    
        當為"rec result"時即為錄音模式，此模式會執行REC_SECOND 後中斷。 REC_SECOND 為錄音秒數，REC_WAV_NAME 為錄音名稱。
        當為"play result"時即為撥放模式，此模式會持續執行直到手動中斷程式。會透過播放裝置將處理後訊號撥出。

    2. ```RATE``` : 取樣頻率
    3. ```CHUNK``` : 每次callback擷取訊號長度 (frame)
    4. ```REC_CHANNEL``` : 輸入channle數，須符合目前選擇輸入設備ch數量
    5. ```PLAY_CHANNEL```: 輸出channle數，須符合目前選擇輸出設備ch數量

* 演算法程式撰寫注意:
    需使用 overlap 的方式進行程式撰寫，否則可能會造成 CHUNK 間有不連續感。
    