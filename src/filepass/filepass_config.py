from enum import Enum


# Define Enum for methods in Filepass
class FilepassMethod(str, Enum):
    SFTP = "sftp"
    SMB = "smb"
    LOCAL = "local"


class ConnectionDetails:
    def __init__(
        self,
        method: FilepassMethod,
        user=None,
        password=None,
        server=None,
        port=None,
        dir=None,
        share=None,
    ):
        self.method = method
        self.user = user
        self.password = password
        self.server = server
        self.port = port
        self.dir = dir
        self.share = share
        # Ensure all required values are provided
        self._validate_parameters()

    # Validate parameter values provided to Connection Objects and raise errors if required.
    def _validate_parameters(self):
        # Validate LOCAL connection details, required fields: 'dir'
        if self.method == FilepassMethod.LOCAL:
            if not self.dir:
                raise ValueError(f"{self.method.name} connection requires 'dir' .")

        # Validate SFTP connection deatils, required fields: 'user', 'password', 'server', 'dir', 'port'.
        # If port number is not defined, revert to default value - '22'

        # Validate SMB connection details, required fields: 'user', 'password', 'server', 'dir', 'share', 'port'.
        # If port number not defined , revert to default value - '445'
        elif self.method in [FilepassMethod.SMB, FilepassMethod.SFTP]:
            if not self.user:
                raise ValueError("(user) value missing (required). ", self.user)

            if not self.password:
                raise ValueError("(password) value missing (required)", self.password)

            if not self.dir:
                raise ValueError("Directory (dir) value missing (required)", self.dir)

            if not self.server:
                raise ValueError("(server) value missing (required) ", self.server)

            if not self.port:
                if self.method == FilepassMethod.SMB:
                    self.port = 445

                else:
                    self.port = 22

            if self.method == FilepassMethod.SMB and not self.share:
                raise ValueError(
                    "SMBShare (share) value missing (required)", self.share
                )

        # Validate Filepass method called
        else:
            raise ValueError(
                f"Unsupported Connection Method: {self.method}. \n Please choose a supported method: SFTP, SMB or LOCAL."
            )
