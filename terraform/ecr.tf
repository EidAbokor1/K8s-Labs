resource "aws_ecr_repository" "app-hub" {
  name                 = "platform-status"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
  encryption_configuration {
    encryption_type = "KMS"
  }

  tags = local.tags

}
