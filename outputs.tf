output "console_log" {
  description = "The console logs from python script execution."
  value       = data.local_file.console_log_file.content
}
/*
output "pi_image_operation_results" {
  description = "The log object that contains all the accounts and their workspaces for which the image import/delete requests were success, skipped and failed."
  value       = local.pi_image_operation_results
}

output "pi_image_status_results" {
  description = "The log object that contains all the accounts and their workspaces for which the provided image is active and inactive."
  value       = local.pi_image_status_results
}
*/
