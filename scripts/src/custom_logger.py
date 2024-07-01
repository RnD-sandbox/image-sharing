class ImageShareLogger:
    """
    A logger for tracking image import/delete operations with success, skipped or failure states.
    """

    def __init__(self):
        self.success_list = []
        self.skipped_list = []
        self.failed_list = []
        self.other = []

    def log_success(self, workspace):
        self.success_list.append({"id": workspace["id"], "name": workspace["name"]})

    def log_skipped(self, workspace):
        self.skipped_list.append({"id": workspace["id"], "name": workspace["name"]})

    def log_failure(self, workspace, error):
        self.failed_list.append(
            {"id": workspace["id"], "name": workspace["name"], "error": error}
        )

    def log_other(self, account, workspace, error):
        log = {
            "account_id": account["account_id"],
            "account_name": account["name"],
            "error": error,
        }
        if workspace != None:
            log["workspace_id"] = workspace["id"]
            log["workspace_name"] = workspace["name"]
        self.other.append(log)

    def get_log(self):
        return {
            "success": self.success_list,
            "skipped": self.skipped_list,
            "failed": self.failed_list,
            "other": self.other,
        }


class ImageStatusLogger:
    """
    A logger for tracking boot image states(active/inactive) and other issues.
    """

    def __init__(self):
        self.active = []
        self.inactive = []
        self.other = []

    def log_active(self, account):
        self.success_list.append(account)

    def log_inactive(self, account):
        self.failed_list.append(account)

    def get_log(self):
        return {"active_images": self.active, "inactive_images": self.inactive}


def merge_image_op_logs(account_level_logs):
    """
    Merge logs from multiprocessing into a final log dictionary.

    Args:
        logs (list): A list of dictionaries containing logs to be merged.

    Returns:
        dict: A dictionary containing merged active and inactive logs.
    """
    final_log = {
        "success": [],
        "skipped": [],
        "failed": [],
        "other": [],
    }
    for log in account_level_logs:
        final_log["success"].extend(log["success"])
        final_log["skipped"].extend(log["skipped"])
        final_log["failed"].extend(log["failed"])
        final_log["other"].extend(log["other"])
    return final_log


def log_account_level_image_op(account_logger, workspace_logger, account):
    """
    Group the image import statuses from workspaces of an account with account information.

    Args:
        account_logger (Logger): The logger to log account-level statuses.
        workspace_logger (Logger): The logger containing workspace-level statuses.
        account (dict): The account information.

    Returns:
        dict: The updated account-level log.
    """
    if workspace_logger:
        if workspace_logger.success_list:
            account_logger.success_list.append(
                {
                    "id": account["account_id"],
                    "name": account["name"],
                    "workspaces": workspace_logger.success_list,
                }
            )
        if workspace_logger.skipped_list:
            account_logger.skipped_list.append(
                {
                    "id": account["account_id"],
                    "name": account["name"],
                    "workspaces": workspace_logger.skipped_list,
                }
            )
        if workspace_logger.failed_list:
            account_logger.failed_list.append(
                {
                    "id": account["account_id"],
                    "name": account["name"],
                    "workspaces": workspace_logger.failed_list,
                }
            )
    return account_logger.get_log()


def merge_status_logs(account_level_logs):
    """
    Merge logs from multiprocessing into a final log dictionary.

    Args:
        logs (list): A list of dictionaries containing logs to be merged.

    Returns:
        dict: A dictionary containing merged active and inactive logs.
    """
    final_log = {"active_images": [], "inactive_images": []}
    for log in account_level_logs:
        final_log["active_images"].extend(log["active_images"])
        final_log["inactive_images"].extend(log["inactive_images"])
    return final_log


def log_account_level_status(account_logger, workspace_logger, account):
    """
    Group the image import statuses from workspaces of an account with account information.

    Args:
        account_logger (Logger): The logger to log account-level statuses.
        workspace_logger (Logger): The logger containing workspace-level statuses.
        account (dict): The account information.

    Returns:
        dict: The updated account-level log.
    """
    if workspace_logger:
        if workspace_logger.active:
            account_logger.active.append(
                {
                    "id": account["account_id"],
                    "name": account["name"],
                    "workspaces": workspace_logger.active,
                }
            )
        if workspace_logger.inactive:
            account_logger.inactive.append(
                {
                    "id": account["account_id"],
                    "name": account["name"],
                    "workspaces": workspace_logger.inactive,
                }
            )
    return account_logger.get_log()
