output "pi_image_operation_results" {
  description = "The log object that contains all the accounts and their workspaces for which the image import/delete requests were success, skipped and failed."
  value       = local.pi_image_operation_results
}

output "pi_image_status_results" {
  description = "The log object that contains all the accounts and their workspaces for which the provided image is active and inactive."
  value       = local.pi_image_status_results
}
