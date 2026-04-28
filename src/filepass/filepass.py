from .filepass_config import ConnectionDetails
from .transports import make_transport
from .watchdog import PER_FILE_TIMEOUT, run_with_timeout


def _safe_close(transport, logger):
    try:
        transport.close()
    except Exception as e:
        logger.warning(f"Error during transport close: {e}")


def _process_one(
    from_t,
    to_t,
    name,
    existing_dest_files,
    from_delete,
    to_delete,
    file_overwrite,
    should_rename,
    new_filename,
    logger,
    index,
    total,
):
    target_name = new_filename if should_rename and new_filename else name

    if to_delete.upper() == "YES" and name in existing_dest_files:
        logger.debug(f"[{index}/{total}] delete (to): {name}")
        try:
            to_t.delete(name)
            existing_dest_files.discard(name)
        except FileNotFoundError:
            logger.warning(f"[{index}/{total}] (To) file ResourceNotFound: {name}")
    else:
        logger.debug(f"[{index}/{total}] No delete (to): {name}")

    if file_overwrite.upper() == "NO" and name in existing_dest_files:
        logger.debug(
            f"[{index}/{total}] File overwrite is disabled. File {name} not transferred"
        )
        return

    with from_t.open_read(name) as src:
        to_t.write(target_name, src)
    logger.debug(f"[{index}/{total}] Transferred: {name}")
    existing_dest_files.add(name)

    if from_delete.upper() == "YES":
        logger.debug(f"[{index}/{total}] delete (from): {name}")
        try:
            from_t.delete(name)
        except FileNotFoundError:
            logger.warning(f"[{index}/{total}] ResourceNotFound: {name}")
    else:
        logger.debug(f"[{index}/{total}] No delete (from): {name}")


def file_pass(
    logger,
    from_conn: ConnectionDetails,
    from_delete,
    from_filter,
    to_conn: ConnectionDetails,
    to_delete,
    file_overwrite,
    new_filename=None,
):
    from_t = make_transport(from_conn, logger)
    to_t = make_transport(to_conn, logger)

    try:
        logger.debug(
            f"Establishing {from_conn.method} connection from server: {from_conn.server}\n Directory: {from_conn.dir}"
        )
        logger.debug(
            f"Establishing {to_conn.method} connection from server: {to_conn.server}\n Directory: {to_conn.dir}"
        )

        total_files = from_t.list(from_filter)
        total_count = len(total_files)
        logger.debug(f"Found {total_count} file(s) to process")

        # Pre-fetch destination listing to avoid per-file network round-trips.
        existing_dest_files = set(to_t.list("*"))

        for index, name in enumerate(total_files, start=1):
            logger.debug(f"[{index}/{total_count}] File to move: {name}")

            should_rename = total_count == 1 and bool(new_filename)

            run_with_timeout(
                _process_one,
                PER_FILE_TIMEOUT,
                from_t,
                to_t,
                name,
                existing_dest_files,
                from_delete,
                to_delete,
                file_overwrite,
                should_rename,
                new_filename,
                logger,
                index,
                total_count,
                _label=f"transfer of {name} [{index}/{total_count}]",
            )

        logger.debug(f"Completed processing {total_count} file(s)")
    finally:
        _safe_close(from_t, logger)
        _safe_close(to_t, logger)
