# Learning Log
This document is intended to record the items that I learned while working on this project. Each entry will include a date in which project work was recorded and the information that was learned during this session. 

## Project Setup 

### September 23, 2026
 - Setup the github repo, project skeleton, & environment
 - Learned how to better structure a README file for clarity and brevity

 ## Data Exploration

 ### September 24, 2026
 - Imported the nfl schedules dataframe & conducted preliminary data analysis
 - Practiced using functions to sort & analyzize data to help build my data pipeline knowledge

 ### September 26, 2026
 - Restrucured the data exploration notebook to follow a logical data exploration structure
 - Learned what the .crosstab pandas function does
    - Counts how often each combination of categories occurs together
    - Returns a DataFrame where the grouped counts are structured into a table

### September 27, 2026
- Worked on sections 4-7 of the data exploration notebook
- Learned how to replace values in a column of a dataframe with a dictionary
   - {Old value: New value}
   - 'df[colum_name].replace(dictionary)
   - the 'home_win' column not scores with proper Elo S ratings
   - built a clean table called 'games_clean' (3,829 games, 21 columns)