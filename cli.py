import logging
import os
import sys

import graypy

from src.filepass import ConnectionDetails, FilepassMethod, file_pass


def main():
    # Load Environmental Variables

    """
    Assign environment variabled to call the desired method for file transfer.
    Can also opt to use the method directly such as:
    from_conn = ConnectionDetails(
         method = FilepassMethod.SMB
    )
    """
    from_protocol = os.environ.get("FROMMETHOD").upper()

    if from_protocol == "SMB":
        from_method = FilepassMethod.SMB
    elif from_protocol == "SFTP":
        from_method = FilepassMethod.SFTP
    elif from_protocol == "LOCAL":
        from_method = FilepassMethod.LOCAL
    else:
        raise ValueError(
            f"Unsupported Connection Method from: {from_protocol}. \n Please choose a supported method: SFTP, SMB or LOCAL."
        )

    to_protocol = os.environ.get("TOMETHOD").upper()

    if to_protocol == "SMB":
        to_method = FilepassMethod.SMB
    elif to_protocol == "SFTP":
        to_method = FilepassMethod.SFTP
    elif to_protocol == "LOCAL":
        to_method = FilepassMethod.LOCAL
    else:
        raise ValueError(
            f"Unsupported Connection Method to: {to_protocol}. \n Please choose a supported method: SFTP, SMB or LOCAL."
        )

    # Connection objects
    from_conn = ConnectionDetails(
        method=from_method,
        user=os.environ.get("FROMUSER"),
        password=os.environ.get("FROMPW"),
        server=os.environ.get("FROMSVR"),
        port=os.environ.get("FROMPORT"),
        dir=os.environ.get("FROMDIR"),
        share=os.environ.get("FROMSMBSHARE"),
    )

    to_conn = ConnectionDetails(
        method=to_method,
        user=os.environ.get("TOUSER"),
        password=os.environ.get("TOPW"),
        server=os.environ.get("TOSVR"),
        port=os.environ.get("TOPORT"),
        dir=os.environ.get("TODIR"),
        share=os.environ.get("TOSMBSHARE"),
    )

    # Parameters required by file_pass
    from_delete = os.environ.get("FROMDELETE")
    from_filter = os.environ.get("FROMFILEFILTER")
    to_delete = os.environ.get("TODELETE")
    new_filename = os.environ.get("NEW_FILENAME")
    file_overwrite = os.environ.get("FILE_OVERWRITE")

    filepass_logger = logging.getLogger("filepass_logger")
    filepass_logger.setLevel(logging.DEBUG)

    # Check if GRAYLOG SERVER configurations are set and add handler accordingly
    if os.environ.get("GRAYLOG_SERVER") and os.environ.get("GRAYLOG_PORT") is not None:
        handler = graypy.GELFTCPHandler(
            os.environ.get("GRAYLOG_SERVER"), int(os.environ.get("GRAYLOG_PORT"))
        )
        filepass_logger.addHandler(handler)

    handler_std = logging.StreamHandler(sys.stdout)
    filepass_logger.addHandler(handler_std)

    logger = logging.LoggerAdapter(
        filepass_logger,
        {
            "from_conn": from_conn,
            "from_delete": from_delete,
            "from_filter": from_filter,
            "to_conn": to_conn,
            "to_delete": to_delete,
            "integration": "filepass",
            "filepass_name": os.environ.get("INTEGRATION_NAME"),
            "file_overwrite": file_overwrite,
            "new_filename": new_filename,
        },
    )
    try:
        file_pass(
            logger,
            from_conn,
            from_delete,
            from_filter,
            to_conn,
            to_delete,
            file_overwrite,
            new_filename,
        )
    except:
        logger.exception("Critical error found", stack_info=True)


if __name__ == "__main__":
    main()
