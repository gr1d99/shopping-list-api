[![Build Status](https://travis-ci.org/gr1d99/shopping-list-api.svg?branch=challenge-3)](https://travis-ci.org/gr1d99/shopping-list-api)  [![Coverage Status](https://coveralls.io/repos/github/gr1d99/shopping-list-api/badge.svg?branch=challenge-3)](https://coveralls.io/github/gr1d99/shopping-list-api?branch=challenge-3)  [![Code Climate](https://codeclimate.com/github/gr1d99/shopping-list-api/badges/gpa.svg)](https://codeclimate.com/github/gr1d99/shopping-list-api) [![Issue Count](https://codeclimate.com/github/gr1d99/shopping-list-api/badges/issue_count.svg)](https://codeclimate.com/shopping-list-api) 

# shopping-list-api
A RESTful ai Flask powered web application that allows users to record and share things they want to spend money on and keeping track of their shopping lists 

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 
See deployment for notes on how to deploy the project on a live system.

## Demo
[Shoppinglist-api](https://shoppinglistapiapp.herokuapp.com)


Take me to [pookie](#pookie)



## Authentication Endpoints

1. **User Registration**

 * **URL**

   `/users/register`

 * **Method:**

   `POST`

 * **Data Format**

   `application/json`
  
 * **Required**

     * `username`
     * `email`
     * `password`
  

 * **Success Response:**

   * **Code:** 201 CREATED
   * **Content:** 
  
         {status :"success", message : "Account created, login with your email and password to get your access tokens" }
 
 * **Error Response:**
  
   * **Code:** 422 UNPROCESSABLE ENTITY
   * **Content:** 
       
         {
             "messages": {
                 "email": [
                   "Missing data for required field."
                 ],
                 "username": [
                   "Missing data for required field."
                 ],
                 "password": [
                   "Missing data for required field."
                 ]
             }
         }
        
        
   OR
    
   * **Code:** 409 CONFLICT
   * **Content:** 
                 
         { error: "username exists" }
         { error: "email exists" 
 
 2. **Login User**
    
