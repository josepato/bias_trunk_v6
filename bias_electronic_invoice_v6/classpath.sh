#! /bin/sh


path=$(pwd)
for item in $(ls $path/axis2/*.jar); do 
echo $item
echo export CLASSPATH=${CLASSPATH}:$item 
done