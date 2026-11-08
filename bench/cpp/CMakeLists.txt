cmake_minimum_required(VERSION 3.20)
project(bin_serializer_cpp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Benchmarks are meaningless without optimizations.
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()

option(BENCH_NATIVE "Compile with -march=native" OFF)
if(BENCH_NATIVE)
    add_compile_options(-march=native)
endif()

# ---------------------------------------------------------------------------
# Code generation: rerun the Python generator whenever the schema, templates
# or generator sources change.
# ---------------------------------------------------------------------------
get_filename_component(REPO_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../.." ABSOLUTE)
set(BENCH_SCHEMA "${CMAKE_CURRENT_SOURCE_DIR}/../bench_schemas.yaml"
    CACHE FILEPATH "Schema used to generate benchmark code")
set(GEN_DIR "${CMAKE_CURRENT_BINARY_DIR}/generated")

find_program(UV uv REQUIRED)

file(GLOB GENERATOR_SOURCES CONFIGURE_DEPENDS
    "${REPO_ROOT}/src/serializer/*.py"
    "${REPO_ROOT}/src/serializer/templates/cpp/*.j2")

set(GENERATED_HEADERS
    "${GEN_DIR}/schemas.hpp"
    "${GEN_DIR}/serializer.hpp"
    "${GEN_DIR}/deserializer.hpp")

add_custom_command(
    OUTPUT ${GENERATED_HEADERS}
    COMMAND "${UV}" run --project "${REPO_ROOT}"
            schema-serializer "${BENCH_SCHEMA}" -o "${GEN_DIR}" -t cpp
    DEPENDS "${BENCH_SCHEMA}" ${GENERATOR_SOURCES}
    WORKING_DIRECTORY "${REPO_ROOT}"
    COMMENT "Generating C++ serializers from ${BENCH_SCHEMA}"
    VERBATIM)
add_custom_target(generate_cpp DEPENDS ${GENERATED_HEADERS})

add_library(generated INTERFACE)
target_include_directories(generated INTERFACE "${GEN_DIR}")
add_dependencies(generated generate_cpp)

# ---------------------------------------------------------------------------
# Google Benchmark: use a system install if present, otherwise fetch it.
# ---------------------------------------------------------------------------
find_package(benchmark 1.8 QUIET)
if(NOT benchmark_FOUND)
    include(FetchContent)
    set(BENCHMARK_ENABLE_TESTING OFF CACHE BOOL "" FORCE)
    set(BENCHMARK_ENABLE_GTEST_TESTS OFF CACHE BOOL "" FORCE)
    set(BENCHMARK_ENABLE_INSTALL OFF CACHE BOOL "" FORCE)
    FetchContent_Declare(
        benchmark
        GIT_REPOSITORY https://github.com/google/benchmark.git
        GIT_TAG v1.9.1
        GIT_SHALLOW TRUE)
    FetchContent_MakeAvailable(benchmark)
endif()

# ---------------------------------------------------------------------------
# Benchmarks
# ---------------------------------------------------------------------------
foreach(bench serialize_bench udp_bench)
    add_executable(${bench} ${bench}.cpp)
    target_link_libraries(${bench} PRIVATE generated benchmark::benchmark_main)
    target_compile_options(${bench} PRIVATE -Wall -Wextra -Wpedantic)
endforeach()
