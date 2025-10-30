# outputs.tf

output "instance_ip" {
  description = "Public IP of the chatbot backend"
  value       = aws_instance.chatbot_server.public_ip
}
