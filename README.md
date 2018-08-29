## pygdfCrossfilter Server

Sample UI:

![sample image](sample-ui.png)

Profiling:

https://docs.google.com/spreadsheets/d/1xYSqHvQrnVlokcvBjQtTAmzX1O8cFTMGUN8NP-tqMhA/edit?usp=sharing


To build using Docker:

while in the directory, run the following commands:
(you should already have pygdf image in your local system)

<pre>
sudo docker build -t athorve/viz .
sudo docker run --runtime=nvidia  -d -p 3000:3000 --name Rapids_viz athorve/viz

</pre>
