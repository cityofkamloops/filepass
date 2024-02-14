import logging
import os
import sys

import graypy

from src.filepass import file_pass


def main():
    # Load Environmental Variables

    # GREYLOG_SERVER
    # GREYLOG_PORT
    # INTEGRATION_NAME

    from_user = os.environ.get("FROMUSER")
    from_pw = os.environ.get("FROMPW")
    from_svr = os.environ.get("FROMSVR")
    from_port = os.environ.get("FROMPORT")
    from_dir = os.environ.get("FROMDIR")
    from_share = os.environ.get("FROMSMBSHARE")
    from_method = os.environ.get("FROMMETHOD")
    from_delete = os.environ.get("FROMDELETE")
    from_filter = os.environ.get("FROMFILEFILTER")

    to_user = os.environ.get("TOUSER")
    to_pw = os.environ.get("TOPW")
    to_svr = os.environ.get("TOSVR")
    to_port = os.environ.get("TOPORT")
    to_dir = os.environ.get("TODIR")
    to_share = os.environ.get("TOSMBSHARE")
    to_method = os.environ.get("TOMETHOD")
    to_delete = os.environ.get("TODELETE")
    # Environment variable added for filename change in single file mode
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
            "from_method": from_method,
            "from_user": from_user,
            "from_svr": from_svr,
            "from_port": from_port,
            "from_share": from_share,
            "from_dir": from_dir,
            "from_filter": from_filter,
            "to_method": to_method,
            "to_user": to_user,
            "to_svr": to_svr,
            "to_port": to_port,
            "to_share": to_share,
            "to_dir": to_dir,
            "integration": "filepass",
            "filepass_name": os.environ.get("INTEGRATION_NAME"),
            "new_filename": new_filename,
        },
    )
    try:
        file_pass(
            logger,
            from_user,
            from_pw,
            from_svr,
            from_port,
            from_dir,
            from_share,
            from_method,
            from_delete,
            from_filter,
            to_user,
            to_pw,
            to_svr,
            to_port,
            to_dir,
            to_share,
            to_method,
            to_delete,
            new_filename,
        )
    except:
        logger.exception("Critical error found", stack_info=True)


if __name__ == "__main__":
    main()
