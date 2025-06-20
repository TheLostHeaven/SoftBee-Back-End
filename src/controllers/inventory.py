from ..models.inventory import InventoryModel

class InventoryController:
    def __init__(self, db):
        self.db = db
        self.model = InventoryModel

    def create_item(self, user_id, item_name, quantity=0, unit='unit'):
        """Creates a new inventory item for a user"""
        return self.model.create(self.db, user_id, item_name, quantity, unit)

    def get_item(self, item_id):
        """Gets inventory item by ID"""
        return self.model.get_by_id(self.db, item_id)

    def get_user_items(self, user_id):
        """Gets all inventory items for a user"""
        return self.model.get_all(self.db, user_id)

    def update_item(self, item_id, **kwargs):
        """Updates inventory item information"""
        self.model.update(self.db, item_id, **kwargs)

    def delete_item(self, item_id):
        """Deletes an inventory item"""
        self.model.delete(self.db, item_id)

    def delete_by_name(self, user_id, item_name):
        """Deletes inventory item(s) by name for a user"""
        self.model.delete_by_name(self.db, user_id, item_name)

    def search_items(self, user_id, item_name):
        """Searches inventory items by name for a user"""
        return self.model.get_by_name(self.db, user_id, item_name)

    def adjust_quantity(self, item_id, amount):
        """Adjusts inventory quantity by amount"""
        self.model.adjust_quantity(self.db, item_id, amount)
