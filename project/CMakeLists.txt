cmake_minimum_required(VERSION 2.8)
project("ECE1508 Project")

find_package( Boost REQUIRED COMPONENTS program_options)

add_executable( spa spa.cc )
target_link_libraries( spa ${Boost_LIBRARIES} )

add_executable( window window.cc )
target_link_libraries( window ${Boost_LIBRARIES} )
