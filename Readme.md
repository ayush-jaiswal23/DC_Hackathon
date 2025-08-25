This is ACSII image art generator.
Technology Used:
Frontend: HTML , TailwindCSS
Backend: Flask
libraries: pillow

In this project user can upload the grayscale png image that is being processed and compressed by algorithm where the image is converted into binary file using pillow and then the pixel value is checked to cluster them in three categories that is Black, white and gray. Then the color is stored in form of pattern like(!,#,$,%,^,&) and then consecutive same pattern are stored (########) to (#007) as an constraint (<=999) and then the compressed string from backend is passed to frontend to display.

Contributors:
Ayush Jaiswal
Kartik Gurjar 
