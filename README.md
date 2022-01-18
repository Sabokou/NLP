# NLP

The "Learning Forest" was developed in the course of an NLP project at DHBW Mannheim by the following team members:

- Alina Buss (4163246)
- Andreas Dichter (6104795)
- Can Berkil (2087362)
- Paula Hölterhoff (9633299)
- Phillip Lange (5920414)
- Simon Schmid (9917195)

**Development Teams**
- Webapp (Alina Buss, Andreas Dichter)
- Answer-Checker (Can Berkil, Simon Schmid)
- Question-Generator (Paula Hölterhoff, Phillip Lange)

**Setup**
1. install docker (including docker-compose)
2. navigate to NLP/webapp/app
3. run "docker-compose up"
    - the build process may take a while
4. Once done you can navigate to "localhost:5000" in your browser

**Using the webapp**
1. upload your document (.docx)
    - be sure that your document follows the needed structure
    - you can also use our example (example-computaional-linguistics.docx)
    - the question generation can take 1-3min depending on your hardware
2. now you can use the learning and exercise pages as much as you want!

** **
**If you want to take a closer look at the database...** 
#### ...you can use the tool adminer that we have implented in the container
1. navigate to "localhost:1234" in your browser
2. choose "PostgreSQL"
3. log in withe following data:
    - User: "postgres"
    - Password: "securepwd"