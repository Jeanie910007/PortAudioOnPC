cmake_minimum_required(VERSION 3.0.0)
project(portaudio_demo VERSION 0.1.0)

include(CTest)
enable_testing()

set(SrcPath "src")
link_directories(${SrcPath})
set(LibPath "lib")
link_directories(${LibPath})
add_executable(portaudio_demo main.c)
target_link_libraries(portaudio_demo portaudio)
target_link_libraries(portaudio_demo sndfile)

set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})
include(CPack)
