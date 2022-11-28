# BeNotReal
#### Video Demo:  https://www.loom.com/share/6a3a88e8ccff421d97c0948fa4c42ce3
#### Description:
So this project is a BeReal knockoff. It is a web-application made  with python (flask), HTML, CSS (Bootstrap) and a little bit of JS.
I chose this stak, because I'm the most familiar with this.

So all python libraries are included in requirements.txt, the flask web-application is in app.py which uses functions  that can be found in helpers.py. The static folder is for my JS/CSS andimages and the HTMLfiles can be found in the templates folder.

### app.py
So this is the web-app hoster. You'll find how the server acts in this file.
Firstly we import  all libraries and set up the Flask web app and change the settings for sessions.
So the  function is what the server will do for the root directory. As you see it requires the client to be logged in first and will redirect the client to /login if that isn't the case. Elsethe person will be redirectedto the /friends directory.

Now we have the login system that works in 2 ways. The number submittion and the sms verification code submission.
Firstly we ask the client for their number, so we can connect the BeReal API and send the user a code through BeReal's API.
Secondly we submit the sms and check if that sms is correct. Ifit is we send the  client some cookies we'll later use for other functionalities such as their authentication token.

Now ofcourse we have a logout function that basically clears all cookies and redirects to client to the login page.

Now we a predifined get_feed function, which will either get the friend feed or the discovery feed depending on the arguments. I chose to do it this way, because the code for the friend feed is very similar to the discovery feed and I wanted the code to be as clean as possible.

The get_feed function requests the given feed from the BeReal API using functions in helpers.py. It then uses the json feed to generate the webpage using jinja2 templates in '/templates/'.
It also supports POST requests for adding comments to users BeReals and sending users on the discovery page friend requests.

All these BeReal API requests are in found in 'helpers.py'.

### helpers.py
So firstly we import all needed libraries

Then we have our function that handles the login reuirement onthe needed pages.

Now  we're getting into the BeReal API functions. These are all found using mitm proxy and an iphone using IOS 13. Then the API calls were built in postman and imported and built into this python file.
So we have a whole dictionary of bereal api endpoints, that we got saved.

The first function is to request a sms verification code from BeReal. We'll require  a phone number, which is given in the login page.

Then we have a submit code function that lets the user submit the code he/she receives. We'll have to use the request id we got sent from the sms request call however. Else the server won't know for which user we're submitting a code. Then we check the server response and send another request if everything went correct to get the authentication token for this user. With this we can do everything we want.

The problem however is that these auth tokens expire in an hour. So using the next function we can refresh our tokens after our old ones have expired without having to login again.

After we have our tokens inplace we can start requesting our feed. In the next functions we do API calls for the discovery and friends feed. Then we return the json body response if everything went correctly. This json will be used by our templates to build a web-page.

Now we have  function that lets us comment on our friends posts ONLY, since we cant comment on random peoples post. For this we'll need the userId of the person we want to omment on, the comment and our auth token. Then we simply send the request and if everything is okay the comment will appear now.

After we have a function that handles sending friend request t0 strangers onour discovery feed.

Now we're done with the BeReal API functions, we have a get location function. Sometimes users share their location and sometimes not. If they do however we want to see what the city and country is that they shared using their longitudes and latitudes.

### /templates

I won't go in too much detail, because everything kind of speaks for itself, however I want to explain how I structured this.

So I have 'layout.html' which is the 'main' file and I just pop in the body.
The body is different for every page and can be found in their file.

For the feeds I have a file/template 'feed.html' Which basically builds the whole feed and then loops through the json feed we talked about earlier. We use that by looping through every post and using 'post-layout.html' for each post. That way its very easy to make changes and apply it everywhere. Therefore there is a smaller post which is either blocked to see if the client hasn't posted yet (will stil be able to see other posts) or their own post if they have posted.

I used a lot of Jinja syntax to make sure everything is functional to what the user requested.

### JS
So with JS I made a couple of small implementations to put the cherry on top of the cake.
The first function makes the flash messages fade out and dissapear.
The second function places the clients own post inside the first smaller post if it exists.
The last function switches the images in posts if clicked on. This is a neat functionality bereals app also has.

All these functions run if DOM is loaded, which means if the webpage is fully loaded.

### CSS
I mainly used bootstrap to style and build the application, however there were some small things I wanted to change which I used the '/static/styles.css' file for.