# Udacity Full Stack Developer Muli-User Blog Project

This project is built using Google App Engine and Python 2.7.  Jinja2 is the
template language used.  

It was built to as part of the Udacity Full-Stack Nanodegree program and is
meant to meet this rubric - [https://review.udacity.com/#!/rubrics/150/view].

The webapp can be run at the following address - [https://blog-147915.appspot.com/] 

The project is a simple multi-user blog that allows users to create accounts.
A logged in user can create, edit, comment on, and like posts.  If a user is not
logged in the app will redirect to the sign-up page.

## Navigation
    From all pages the Main page title can be clicked to navigate back to the
    main blog page.  All other navigation is accomplished through links

## GAE Entities:
    1. Post
      * Contains main post content - author, content, created, subject, likes
    2. User
      * Contains information obtained from signup form plus password hash
    3. Liker
      * used to establish a one to many relationship between a Post and Users
        who have liked the post
    4. Comment
      * used to establish a one to many relationship between a Post and Comments
        associated with that post.

## Templates:
    1. Base.html
      * home link - redirects to main Blog page
      * newpost link - redirects to newpost form
    2. signup-form.html
      * for creating a new user account
    3. login-form.html
      * for returning users to log in
    4. front.html
      * renders posts and comments
    5. post.html
      * fills in the post when post.render is called from front.html
    6. post-form.html
      * form for creating a new post
    7. permalink.html
      * after a new post is created this page is displayed
    8. edit-post.html
    9. comment-form.html
        * create a new comment
    10. comment.html
        * for rendering within front.html
    11. edit-comment.html


        
