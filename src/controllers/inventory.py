from ..models.inventory import InventoryModel

class InventoryController:
    def __init__(self, db):
        self.db = db
        self.model = InventoryModel

    def create_item(self, apiary_id, item_name, quantity=0, unit='unit'):
        """Creates a new inventory item for an apiary"""
        return self.model.create(self.db, apiary_id, item_name, quantity, unit)

    def get_item(self, item_id):
        """Gets inventory item by ID"""
        return self.model.get_by_id(self.db, item_id)

    def get_apiary_items(self, apiary_id):
        """Gets all inventory items for an apiary"""
        return self.model.get_all(self.db, apiary_id)

    def update_item(self, item_id, **kwargs):
        """Updates inventory item information"""
        self.model.update(self.db, item_id, **kwargs)

    def delete_item(self, item_id):
        """Deletes an inventory item"""
        self.model.delete(self.db, item_id)

    def delete_by_name(self, apiary_id, item_name):
        """Deletes inventory item(s) by name for an apiary"""
        self.model.delete_by_name(self.db, apiary_id, item_name)

    def search_items(self, apiary_id, item_name):
        """Searches inventory items by name for an apiary"""
        return self.model.get_by_name(self.db, apiary_id, item_name)

    def adjust_quantity(self, item_id, amount):
        """Adjusts inventory quantity by amount"""
        self.model.adjust_quantity(self.db, item_id, amount)
