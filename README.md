##App Engine Local Dev Cron Scheduler##


App engine is great, but their python SDK does not include a way to actually execute scheduled cron jobs, other than manually running them from the exposed web interface. This makes development a bit difficult when you rely on the cron jobs to update data models, execute tasks, etc.

This is a simple python script that reads in your cron.yaml file, and uses pythons thread library to schedule, monitor, and execute the jobs defined in your cron.yaml file on your local running instnace of app engine SDK.

*Authored by* [Evan Carothers](https://github.com/ecaroth) @ [Docalytics](https://github.com/orgs/Docalytics/dashboard)


####Usage
To run the script simply call it from the command line with the needed arguments, listed below. It will continue to run until you manually stop the script execution

**ARGS**

* `--gae-path` = *required*,  The full path to your app engine SDK installation. *NOTE - *
* `--app_path` = *required*,  The full path to your app engine application (where your cron.yaml & app.yaml files reside)
* `-app_url` = the URL you access your local app engine app at - *(defaults to http:// localhost:8080)*
* `-disable_logging` = disable verbose output and logging from the script - *(defaults to False)*


**Example Usage:**

	C:\appengine_sdk_cron.py --gae_path "C:\Program Files (x86)\Google\google_appengine" --app_path "C:\MYAPP" --app_url "http://localhost:8081"
    
    
After the script starts running you will see output indicating the scheduling and when your jobs will run, which will continue to update as they are executed, indicating the status of the jobs.

EXAMPLE OUTPUT:

	=== STARTING SCHEDULED EXECUTION OF 5 CRON JOBS ===
    ::JOB AT /workers/my-minute-task-example SCHEDULED TO RUN AT 11/08/14 11:29:02 (in 60 seconds)
    ::JOB AT /workers/my-hourly-task-example SCHEDULED TO RUN AT 11/08/14 12:29:02 (in 3600 seconds)
    ::JOB AT /workers/my-daily-task-example SCHEDULED TO RUN AT 11/09/14 08:00:00 (in 73917 seconds)
    :[11:29AM] Job 'http://docalytics:8081/workers/my-minute-task-example' executed (Success)
    ::JOB AT /workers/my-minute-task-example SCHEDULED TO RUN AT 11/08/14 11:30:02 (in 60 seconds)
        
