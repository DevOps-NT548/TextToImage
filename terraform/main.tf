terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "4.80.0" // Provider version
    }
  }
  required_version = "1.10.2" // Terraform version
}

provider "google" {
  project     = var.project_id
  region      = var.region
  credentials = file("/home/kevvn/Documents/UIT/NT548/Text2Img/namsee_key.json")
}

// Google Kubernetes Engine
resource "google_container_cluster" "primary" {
  name     = "${var.project_id}-gke"
  location = var.region
  remove_default_node_pool = false
  initial_node_count       = 1

  node_config {
    service_account = "namsee@linen-walker-444306-k9.iam.gserviceaccount.com" # Explicitly set a service account
    machine_type = "e2-highmem-4" # Default machine type for new node pools
  }
}

resource "google_container_node_pool" "primary_nodes" {
  name       = "node-pool"
  location   = var.region
  cluster    = google_container_cluster.primary.name
  node_count = 1

  node_config {
    preemptible  = false
    machine_type = "e2-highmem-4" # 4 vCPU + 32 GB memory   
  }
}