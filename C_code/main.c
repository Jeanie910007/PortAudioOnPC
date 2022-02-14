#include "inc/main.h"

int frame_counter = 0;
int finished;
int i;
int j;
static int processCallback(const void *inputBuffer, void *outputBuffer,
                           unsigned long framesPerBuffer,
                           const PaStreamCallbackTimeInfo *timeInfo,
                           PaStreamCallbackFlags statusFlags,
                           void *userData)
{
    paTestData *data = (paTestData *)userData;
    float *rptr = (float *)inputBuffer;
    float *wptr = (float *)outputBuffer;
    float *save_ptr = &data->recordedSamples[data->frameIndex * MIC_CHANNELS];
    /* Prevent unused variable warnings. */
    (void)outputBuffer;
    (void)timeInfo;
    (void)statusFlags;
    (void)inputBuffer;
    long framesToCalc;
    int counter;
    unsigned long framesLeft = (data->maxFrameIndex - data->frameIndex);

    /* check input len */
    if (framesLeft < framesPerBuffer)
    {
        finished = paComplete; // jump out while loop
        return finished;
    }
    else
    {
        framesToCalc = framesPerBuffer;
        finished = paContinue;
    }

    for (i = 0; i < framesToCalc; i++)
    {
        for (j = 0; j < MIC_CHANNELS; j++)
        {
            mic_data[j][data->frameIndex + i] = *rptr++;
            *save_ptr++ = mic_data[j][data->frameIndex + i];
            if (j < 2)
            {
                *wptr++ = mic_data[j][data->frameIndex + i];
            }
        }
    }
    data->frameIndex += framesToCalc;
    return finished;
}

int main(void)
{
    /* PortAudio Parameter */
    PaStreamParameters inputParameters, outputParameters;
    PaStream *stream;
    PaError err = paNoError; /* Init = 0 */
    paTestData data;
    const PaDeviceInfo *deviceInfo;
    int i;
    int numSamples; /*(float) NUM_SECONDS * SAMPLE_RATE * MIC_CHANNELS */
    int numBytes;   /* numSamples * sizeof(float) */

    /* Record array setting */
    data.maxFrameIndex = TOTALFRAMES; /* Record date = (NUM_SECONDS * SAMPLE_RATE) */
    data.frameIndex = 0;              /* first frameIndex */
    numSamples = TOTALSAMPLE;         /* (Record date * mic_num) */
    numBytes = numSamples * sizeof(float);
    data.recordedSamples = (float *)calloc(numSamples, sizeof(float)); /* Record array */

    /*=====================================================================================*/
    /* Start portAudio process */
    /* Input parameter*/

    err = Pa_Initialize();
    inputParameters.device = Pa_GetDefaultInputDevice();
    if (inputParameters.device == paNoDevice)
    {
        fprintf(stderr, "Error: No default input device.\n");
        goto done;
    }
    inputParameters.channelCount = MIC_CHANNELS;
    inputParameters.sampleFormat = paFloat32;
    inputParameters.suggestedLatency = Pa_GetDeviceInfo(inputParameters.device)->defaultLowOutputLatency;
    inputParameters.hostApiSpecificStreamInfo = NULL;

    /*----------------------------------*/
    /* Output parameter*/
    outputParameters.device = Pa_GetDefaultOutputDevice(); /* default output device */
    if (outputParameters.device == paNoDevice)
    {
        fprintf(stderr, "Error: No default output device.\n");
        goto done;
    }
    outputParameters.channelCount = 2;         /* stereo output */
    outputParameters.sampleFormat = paFloat32; /* 32 bit floating point output */
    outputParameters.suggestedLatency = Pa_GetDeviceInfo(outputParameters.device)->defaultLowOutputLatency;
    outputParameters.hostApiSpecificStreamInfo = NULL;
    /*----------------------------------*/
    /* Start Record and play */
    err = Pa_OpenStream(
        &stream,
        &inputParameters,
        &outputParameters,
        SAMPLE_RATE,
        FRAME_NUM,
        paClipOff,
        processCallback,
        &data);
    if (err != paNoError)
        goto done;

    err = Pa_StartStream(stream);
    if (err != paNoError)
        goto done;

    /* It will jump out of the loop when the recording is completed. */
    while ((err = Pa_IsStreamActive(stream)) == 1)
    {
        Pa_Sleep(1000);
        printf("now recording = %.3fs\n", ((float)data.frameIndex / (float)SAMPLE_RATE));
        fflush(stdout);
    }

    err = Pa_StopStream(stream);
    if (err != paNoError)
        goto done;

    err = Pa_CloseStream(stream);
    if (err != paNoError)
        goto done;

    Pa_Terminate();
    printf("Test finished.\n");

    /* SNDFILE Parameter */
    SNDFILE *file;
    SF_INFO sfinfo;

    sfinfo.frames = TOTALSAMPLE;
    sfinfo.samplerate = SAMPLE_RATE;
    sfinfo.channels = MIC_CHANNELS;
    sfinfo.format = (int)(SF_FORMAT_WAV | SF_FORMAT_PCM_16);
    sfinfo.sections = (int)1;
    char out_fname[] = "result/rec_wav.wav";
    file = sf_open(out_fname, SFM_WRITE, &sfinfo);
    sf_write_float(file, data.recordedSamples, TOTALSAMPLE);
    sf_close(file);

    if (DATA_TO_TXT)
    {

        FILE *file;
        err = fopen_s(&file, "result/record.txt", "w");
        for (i = 0; i < MIC_CHANNELS; i++)
        {
            fprintf(file, "\nch%d\n\n========================================\n\n", i);
            for (j = 0; j < NUM_SECONDS * SAMPLE_RATE; j++)
            {
                fprintf(file, "%f\n", mic_data[i][j]);
            }
        }
    }

done:
    Pa_Terminate();
    if (data.recordedSamples) /* Sure it is NULL or valid. */
        free(data.recordedSamples);
    if (err != paNoError)
    {
        fprintf(stderr, "An error occured while using the portaudio stream\n");
        fprintf(stderr, "Error number: %d\n", err);
        fprintf(stderr, "Error message: %s\n", Pa_GetErrorText(err));
        err = 1; /* Always return 0 or 1, but no other return codes. */
    }
    return err;
}