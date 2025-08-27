from ..models.inventory import InventoryModel

class InventoryController:
    def __init__(self, db):
        self.db = db
        self.model = InventoryModel

    def create_item(self, apiary_id, name, quantity=0, unit='unit', description=None, minimum_stock=0):
        """Creates a new inventory item for an apiary"""
        return self.model.create(self.db, apiary_id, name, quantity, unit, description, minimum_stock)

    def get_item(self, item_id):
        """Gets inventory item by ID"""
        return self.model.get_by_id(self.db, item_id)

    def get_item_with_apiary(self, item_id):
        """Gets inventory item with apiary information"""
        return self.model.get_item_with_apiary(self.db, item_id)

    def get_apiary_items(self, apiary_id):
        """Gets all inventory items for an apiary"""
        return self.model.get_all(self.db, apiary_id)

    def update_item(self, item_id, **kwargs):
        """Updates inventory item information"""
        self.model.update(self.db, item_id, **kwargs)

    def delete_item(self, item_id):
        """Deletes an inventory item"""
        self.model.delete(self.db, item_id)

    def delete_by_name(self, apiary_id, name):
        """Deletes inventory item(s) by name for an apiary"""
        self.model.delete_by_name(self.db, apiary_id, name)

    def search_items(self, apiary_id, name):
        """Searches inventory items by name for an apiary"""
        return self.model.get_by_name(self.db, apiary_id, name)

    def adjust_quantity(self, item_id, amount):
        """Adjusts inventory quantity by amount"""
        self.model.adjust_quantity(self.db, item_id, amount)

    def get_user_inventory(self, user_id):
        """Gets all inventory items from all apiaries belonging to a user"""
        return self.model.get_by_user_id(self.db, user_id)

    def get_low_stock_items(self, apiary_id):
        """Gets items with low stock for an apiary"""
        return self.model.get_low_stock_items(self.db, apiary_id)

    def get_apiary_summary(self, apiary_id):
        """Gets inventory summary for an apiary"""
        return self.model.get_apiary_summary(self.db, apiary_id)

    def validate_user_access(self, item_id, user_id):
        """Validates that user has access to the inventory item through their apiary"""
        return self.model.validate_apiary_access(self.db, item_id, user_id)