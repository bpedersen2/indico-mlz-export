Indico MLZ export
=================


An advanced registration exporter

Usage 
-----

 - Install the plugin in Indico (see indico docs how to install and
enable an extension)

 - Create the client secrets in indico: 
    Administration -> Integration -> Applications
    
    Register the application as: "RegistrationsAPI" 

    + Allowed callback urls: "https://localhost/"

    + Allowed scopes : Event registrants, User information (read only),
Legacy API

    + Enabled : Yes
   
    + Trusted : Yes


Client example (python):

  see api_example directory

  Add URL, client secrets (see step above) and login details ( see comments in code, depends on how your instance is set up).
