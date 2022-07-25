# Steps to generate the cython file

- Make required changes to the .pyx file
- In the command line, run the following commands after navigating to this folder
    - `docker build -t <name> .`
    - `docker run <name>`
- Check the name of the container generated (can be viewed on docker desktop). Then run the following command
    - `docker export <suspect-container> > <suspect-container>.tar`
- Extract ragnaroc.so file present in the tar folder.
- Replace the newly generated `.so` file for the existing one, and you've successfully updated the model. Congratulations! :tada:

We have to follow these steps for making any updates to the RAGNAROC model because cython generates a dll file on a windows machine, whereas linux systems (such as the AWS-EB server) requires a `.so` file.
