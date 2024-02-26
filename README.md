# Filepass Package #

Filepass package is a comprehensive Python package designed to facilitate the transfer of the files across different locations and protocols with ease.
It supports SFTP, SMB, and LOCAL file systems, and offers functionalities like file renaming (in single file mode) and selective file transfer based on assigned filter.
It also offeres advanced file management features such as conditional deletion of files.
With support for both custom handler and local logging, 'Filepass' ensures that you can keep a detailed log of your file trasnfers, making troubleshooting and monitoring a breeze.


## Features ##

- **Multiple Protocols Support**:
Seamlessly transfer files using SFTP, SMB, and LOCAL file systems.

- **Flexible File Selection**:
Use 'from_filter' parameter to specify exactly which files to transfer, supporting both specific filenames and wildcards for multiple files.

- **File Renaming (in single file transfer mode)**
Easily rename files during single file transfer mode.

- **Connection Objects**:
Utilize the pre-defined connnection objects for efficient and secure connections to server.

- **Conditional File Deletion**:
Automatically delete older files at the destination before transfer using 'to_delete', or remove source files after a successful transfer using 'from_delete'.

- **Advanced Logging**:
Enable custom logging handler by defining the server name, port number and adding the handler to the logger defined. Otherwise, default to local logging to stdout for monitoring and troubleshooting.

## Installation ##

pip install filepass

## Quick Start ##
1. Import Filepass package:
    e.g.:
    ```from filepass import file_pass, ConnectionDetails, FilepassMethod```

2. Set up connection - create a connection object (ConnectionDetails) based on your protocol of choice. FilepassMethod offers three protocols: SFTP, SMB, and LOCAL
    e.g.:

        ```python
        sourceServer = ConnectionDetails(
        method=FilepassMethod.SMB,
        user="user",
        password="password",
        server="servername",
        port="portnumber",
        dir="directory/folder",
        share="SMB share",
        )
        destinationServer = ConnectionDetails(
            method=FilepassMethod.SFTP,
            user="user",
            password="password",
            server="servername",
            port="portnumber",
            dir="directory/folder",
        )
        ```


3. Configure Logging:
    (Optional)
    If you want to enable custom handler logging, such as Graylog logging. Set the server details as follows:
    Example: Graylog
        * Import the required library for custom logging - import graypy
        * Add the handler to your defined logger:

            ```python
            handler = graypy. graypy.GELFTCPHandler(
                ("servername"), int("portnumber")
            )
            ```

    If you want to simply use local logging:
        * Import python logging package.
        * Define the logger and handler.
            * E.g., handler = logging.StreamHandler(sys.stdout)
        * Add the handler to your defined logger.

4. Define the required parameters for file transfer:
    * from_filter = "filename/wildcard"
        * e.g.
            ```python
            from_filter = "*.txt"  #transfers all files in the directory, with .txt extension.
            from_filter = "transfer_file.csv"  #transfers the selected file.```
    * to_delete = "yes or no".
    * from_delete = "yes or no".
    * logger = set custom handler or local handler.

5. Rename file in single file transfer mode:
    Rename a file during transfer by specifying the new_filename parameter such as:
    * e.g.,
    ```python
    new_filename = "newfilename"
    ```

    Defaults to 'None', if parameter is not defined.

6. Transfer Files:
    Use the file_pass method to move files to move files from one location to another.
    * e.g.,
        ```python
        file_pass(
            logger,
            from_conn,
            to_conn,
            from_filter,
            to_delete,
            from_delete,
            new_filename,
        )
        ```

## Support ##
If you encounter any issues or have questions, please file an issue on our [GitHub Issues Page](https://github.com/cityofkamloops/filepass/issues)


## Contributing ##
Contributions to Filepass are welcome! Please refer to our [Contribution Guidelines](https://docs.github.com/en/contributing)
### Ways to Contribute ###
    * Submit bug reports and feature requests.
    * Write and improve documentation.
    * Write code for new features and bug fixes.
    * Review pull requests.
    * Enhance the package's test coverage.

### Code of Conduct ###
    - Participation in this project is governed by The City of Kamloops Code of Conduct. We expect everyone to uphold the principles of respect, kindness and cooperation.

### How to submit contributions ###
* Reporting bugs:
    - Use the issue tracker to report bugs.
    - Describe the bug and include steps to reproduce.

* Feature Requests:
    - Submit feature requests using the issue tracker.
    - Please include an explanation why the feature would be useful, and how it should work if possible.

* Pull Requests:
    - Fork the repository and create your branch from 'main'.
    - If you have added code, please include tests.
    - Ensure your project lints and follows the project's coding conventions.
    - Write a clear and descriptive commit message.
    - Open a pull request with a clear title and description.

## Thank you!! ##

### Happy file transferring! ###
