import logging
import os
import sys

import graypy

from src.filepass import ConnectionDetails, file_pass


def main():
    # Load Environmental Variables

    # Connection objects
    from_conn = ConnectionDetails(
        method=os.environ.get("FROMMETHOD"),
        user=os.environ.get("FROMUSER"),
        password=os.environ.get("FROMPW"),
        server=os.environ.get("FROMSVR"),
        port=os.environ.get("FROMPORT"),
        dir=os.environ.get("FROMDIR"),
        share=os.environ.get("FROMSMBSHARE"),
    )

    to_conn = ConnectionDetails(
        method=os.environ.get("TOMETHOD"),
        user=os.environ.get("TOUSER"),
        password=os.environ.get("TOPW"),
        server=os.environ.get("TOSVR"),
        port=os.environ.get("TOPORT"),
        dir=os.environ.get("TODIR"),
        share=os.environ.get("TOSMBSHARE"),
    )

    from_delete = os.environ.get("FROMDELETE")
    from_filter = os.environ.get("FROMFILEFILTER")
    to_delete = os.environ.get("TODELETE")
    new_filename = os.environ.get("NEW_FILENAME")

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
            new_filename,
        )
    except:
        logger.exception("Critical error found", stack_info=True)


if __name__ == "__main__":
    main()
