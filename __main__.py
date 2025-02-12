from pulumi.provider.experimental import Metadata, component_provider_host

if __name__ == "__main__":
    component_provider_host(Metadata(name="gcp-data", version="1.0.0"))