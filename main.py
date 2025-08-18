from src.config.config_manager import ConfigurationManager
from src.data.futures_data_manager import ConfigurableFuturesDataManager


def main():
    """Main entry point for the futures data management system"""

    # Initialize configuration
    config_mgr = ConfigurationManager(
        config_file="config/futures_config.yaml",
        environment="development"
    )

    # Initialize data manager
    data_mgr = ConfigurableFuturesDataManager(config_mgr)

    # Build inventory
    inventory = data_mgr.build_inventory()
    print(f"Found {len(inventory)} instruments")

    # Get roll parameters for ES
    es_roll_params = data_mgr.get_roll_parameters("ES")
    if es_roll_params:
        print(f"ES roll offset: {es_roll_params.roll_offset_days} days")

    # Aggregate and save metadata
    aggregated_meta = data_mgr.aggregate_meta_data()
    data_mgr.save_aggregated_data(aggregated_meta)

    print("System initialization complete!")


if __name__ == "__main__":
    main()