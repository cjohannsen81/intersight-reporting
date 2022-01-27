import intersight.api.storage_api
import intersight.api.compute_api
import credentials
import csv

header = ["model","serial","rack/blade","name","vendor","model","pci_slot","flash_controller","flash_controller_state","vendor","pysical_card_type","physical_card_status","pysical_card_type","physical_card_status"]
data = []

top = 1000
skip = 0

def get_flex_storage(apiClient):
    api_instance = intersight.api.storage_api.StorageApi(apiClient)
    flash_controllers = api_instance.get_storage_flex_flash_controller_list(top=top,skip=skip)
    for fcontroller in flash_controllers.results:
        #uses the compute board moid to gather compute unit data
        compute_board = fcontroller["compute_board"]["moid"]
        get_compute(apiClient,compute_board)
        data.append(fcontroller["model"])
        data.append(fcontroller["controller_state"])
        data.append(fcontroller["vendor"])
        physical_drives = fcontroller["flex_flash_physical_drives"]
        for p_drive in physical_drives:
            physical_drive = p_drive["moid"]
            get_sd_drives(apiClient,physical_drive)
        print(data)
        #writes the data array into the csv file
        with open('sd_info.csv', 'a', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(data)
        data.clear()

def get_sd_drives(apiClient,physical_drive):
    api_instance = intersight.api.storage_api.StorageApi(apiClient)
    flash_drives = api_instance.get_storage_flex_flash_physical_drive_by_moid(physical_drive)
    data.append(flash_drives["card_type"])
    data.append(flash_drives["card_status"])

def get_compute(apiClient,compute_unit):
    api_instance = intersight.api.compute_api.ComputeApi(apiClient)
    summary = api_instance.get_compute_board_by_moid(compute_unit)
    data.append(summary["model"])
    data.append(summary["serial"])
    if summary["compute_rack_unit"]:
        rack_unit = summary["compute_rack_unit"]["moid"]
        mapping = api_instance.get_compute_physical_summary_by_moid(rack_unit)
        data.append("Rack-Server")
        data.append(mapping["name"])
    elif summary["compute_blade"]:
        blade_unit = summary["compute_blade"]["moid"]
        mapping = api_instance.get_compute_physical_summary_by_moid(blade_unit)
        data.append("Blade-Server")
        data.append(mapping["name"])
    storage_controllers = summary["storage_controllers"]
    #kinda weird but it was late and the index() didn't work, servers can have 0,1,2 controller
    number = len(storage_controllers)
    if number == 2:
        print(storage_controllers[0]["moid"])
        moid = storage_controllers[0]["moid"]
        get_storage_controller(apiClient,moid)
        print(storage_controllers[1]["moid"])
        moid = storage_controllers[1]["moid"]
        get_storage_controller(apiClient,moid)
    if number == 1:
        print(storage_controllers[0]["moid"])
        moid = storage_controllers[0]["moid"]
        get_storage_controller(apiClient,moid)
        data.extend(["None","None","None"])
    if number == 0:
        data.extend(["None","None","None","None","None","None"])

def get_storage_controller(apiClient,moid):
    api_instance = intersight.api.storage_api.StorageApi(apiClient)
    storage_controller = api_instance.get_storage_controller_by_moid(moid)
    data.append(storage_controller["vendor"])
    data.append(storage_controller["model"])
    data.append(storage_controller["pci_slot"])

def main():
    apiClient = credentials.config_credentials()
    try:
        with open('sd_info.csv', 'a', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
        get_flex_storage(apiClient)
    except intersight.OpenApiException as e:
        print(e)

if __name__ == "__main__":
    main()
