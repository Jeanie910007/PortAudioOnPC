#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <math.h>
#include "portaudio.h"
#include "sndfile.h"
#define NUM_SECONDS (10)
#define SAMPLE_RATE (16000)
#define FRAME_NUM (512)
#define MIC_CHANNELS (4)
#define TOTALFRAMES (int)(NUM_SECONDS * SAMPLE_RATE)
#define TOTALSAMPLE (int)(NUM_SECONDS * SAMPLE_RATE * MIC_CHANNELS)
#define SAMPLE_SILENCE (0.0f)

#define DATA_TO_WAV 1
#define DATA_TO_TXT 1
typedef struct
{
    int frameIndex;         /* Current recording data points. */
    int maxFrameIndex;      /* Total recording data points. */
    float *recordedSamples; /* Recording data. */
} paTestData;

float mic_data[MIC_CHANNELS][TOTALFRAMES] = {0};