#!/bin/bash

#echo an empty line
echo

# copy the file from the kindle.
# Show the error message if there is a problem copying.
#    * The kindle not being present
#    * TODO: Add more sources of error
cp /media/`whoami`/Kindle/documents/My\ Clippings.txt ./ 2> /dev/null
if [ $? -eq 0 ]; then
    echo Copy from Kindle successul.

    # Move the file to clippings.txt generate error message is not successul.
    mv My\ Clippings.txt clippings.txt 2> /dev/null
    if [ $? -eq 0 ]; then
        echo File rename successful.
    else
        echo ERROR RENAMING FILE.
        echo File saved as \'My Clippings.txt\' instead.
        echo You need to rename this file to \'clippings.txt\' for the program to work
    fi
    
else
    echo ERROR COPYING FILE.
    echo Please make sure that your Kindle is attached and /media/`whoami`/Kindle/documents/My\ Clippings.txt is accessible.
fi

#echo one more empty line
echo