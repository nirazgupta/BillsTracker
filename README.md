# BillsTracker
BillsTracker is a web app developed with purpose of providing users a platform where they can keep track group shared bills and monetary owings among groups. Upon joining the app, users can create or join multiple groups. Users can specify number of people to split a bill with while recording a bill. They are provided with dashboard where they can view the bill, their owings, expenses, and more. App has enforced rules such as a bill can be only deleted by the person who owns the group but can be edited by who recorded the bill, User can only leave a group if he/she has cleared all the bill in the group, group will only be deleted if all the users leaves the group and the app handles this automatically. Note: Apart from features mentioned above, the motive behind this application is to implement Optical Character Recognition(OCR) to scan receipts and automatically record the bill for the user by utilizing Tesseract which an open source OCR library. This feature is not achieved yet because the idea was to implement develop a mobile interface to take picture of the reciepts and send the image to backend via REST API implementation where the receipt would be processed at the backend and the bill would be recorded by the app for the user. The major setback was the underestimation of time for given scopes, manpower limitation. I am continuing to work on the project to implement this feature and will push the app on git hub as well as update the live application once I acheive it. 

# Link to application
* http://billstracker.herokuapp.com/
## Use the following credentials to login if you don't wish to register
* User name: jithu
* Password: test

# Scope
* User registration and authentication
* Create groups
* Join groups to share expenses
* Split transaction between select group members
* Enforce restriction to edit or delete transaction
* Show group bills summary, overall summary
* Show for a transaction, who owes whom and how much
* Data visualizations for groups to see patterns of expenses
* Implement OCR to scan receipts and record the transaction (not implemented yet)

# Technologies used
* Flask
* Angular JS
* Bootstrap
* HTML 
* AJAX 
* JQuery 
* MySQL
* D3.js
* Git
* Tesseract OCR
* D3.js
* Heroku



