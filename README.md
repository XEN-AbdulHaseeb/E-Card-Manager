# BirthDayBOT
BIrthDayBOT is an app that generates and sends a customized jpeg of a birthday card to a loved one on their birthday.

The user will enter the required data into a client, the client will forward the data to a remote server using Socket Programming.

The server will handle the complex operations of generation of the JPEG and scheduling of the email.

# Current Build info

The current build meets the basic specifications I have added some additional features namely:
-The ability to choose fonts and templates.

# Features to be added in future builds
-A preview screen which allows the user to edit the postion, RGB, size of the text of the JPEG\n
-Allow users to upload their own fonts and templates
-Implement Open Authentication

# Major drawbacks
-The app uses an email that has "Less secure app access" enabled which google is going to remove by the end of May 2022, rendering the server obsolete. So OAuth needs to implemented in the future.
