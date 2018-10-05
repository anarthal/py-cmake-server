cmake_minimum_required(VERSION 3.1.0)
project(cmakeservertest)

add_executable(
	cmakeservertest
	src/main.cpp
	src/fun.cpp
)
target_include_directories(
	cmakeservertest
	PRIVATE
	include/
)