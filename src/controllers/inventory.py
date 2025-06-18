from flask import jsonify, current_app
from src.models.inventory import InventoryModel
from src.database.db import get_db

class InventoryController:
    @staticmethod
    def get_all_items():
        """Obtiene todos los items del inventario"""
        db = get_db()
        try:
            items = InventoryModel.get_all_raw(db)
            if not items:
                return {'message': 'No hay items en el inventario'}, 200
            return [dict(item) for item in items], 200
        except Exception as e:
            current_app.logger.error(f"Error al obtener items: {str(e)}")
            return {'error': 'Error interno al obtener los items'}, 500

    @staticmethod
    def get_item(item_id):
        """Obtiene un item específico por ID"""
        db = get_db()
        try:
            if not item_id or not isinstance(item_id, int):
                return {'error': 'ID de item inválido'}, 400
                
            item = InventoryModel.get_by_id_raw(db, item_id)
            if not item:
                return {'error': 'Item no encontrado'}, 404
            return dict(item), 200
        except Exception as e:
            current_app.logger.error(f"Error al obtener item {item_id}: {str(e)}")
            return {'error': 'Error interno al obtener el item'}, 500

    @staticmethod
    def create_item(data):
        """Crea un nuevo item en el inventario"""
        db = get_db()
        try:
            if not data or 'item_name' not in data:
                return {'error': 'El campo "item_name" es obligatorio'}, 400

            item_name = data['item_name'].strip()
            if not item_name:
                return {'error': 'El nombre del item no puede estar vacío'}, 400

            try:
                quantity = int(data.get('quantity', 0))
                if quantity < 0:
                    return {'error': 'La cantidad no puede ser negativa'}, 400
            except ValueError:
                return {'error': 'La cantidad debe ser un número entero'}, 400

            unity = data.get('unity', 'unit').strip()
            if not unity:
                return {'error': 'La unidad no puede estar vacía'}, 400

            existing_items = InventoryModel.get_item_by_name(db, item_name)
            if existing_items:
                for item in existing_items:
                    if item['item_name'].lower() == item_name.lower():
                        return {
                            'error': 'Ya existe un item con este nombre',
                            'existing_item': dict(item)
                        }, 409

            item_id = InventoryModel.create_raw(db, item_name, quantity, unity)
            new_item = InventoryModel.get_by_id_raw(db, item_id)
            return {
                'message': 'Item creado exitosamente',
                'item': dict(new_item)
            }, 201
            
        except Exception as e:
            current_app.logger.error(f"Error al crear item: {str(e)}")
            return {'error': 'Error interno al crear el item'}, 500

    @staticmethod
    def update_item(item_id, data):
        """Actualiza un item existente"""
        db = get_db()
        try:
            if not item_id or not isinstance(item_id, int):
                return {'error': 'ID de item inválido'}, 400
                
            if not data:
                return {'error': 'No se proporcionaron datos para actualizar'}, 400

            existing_item = InventoryModel.get_by_id_raw(db, item_id)
            if not existing_item:
                return {'error': 'Item no encontrado'}, 404

            update_data = {}
            validation_errors = []

            if 'item_name' in data:
                new_name = data['item_name'].strip()
                if not new_name:
                    validation_errors.append('El nombre del item no puede estar vacío')
                else:
                    existing_items = InventoryModel.get_item_by_name(db, new_name)
                    if existing_items:
                        for item in existing_items:
                            if item['id'] != item_id and item['item_name'].lower() == new_name.lower():
                                validation_errors.append('Ya existe otro item con este nombre')
                                break
                    update_data['item_name'] = new_name

            if 'quantity' in data:
                try:
                    quantity = int(data['quantity'])
                    if quantity < 0:
                        validation_errors.append('La cantidad no puede ser negativa')
                    else:
                        update_data['quantity'] = quantity
                except ValueError:
                    validation_errors.append('La cantidad debe ser un número entero')

            if 'unity' in data:
                new_unity = data['unity'].strip()
                if not new_unity:
                    validation_errors.append('La unidad no puede estar vacía')
                else:
                    update_data['unity'] = new_unity

            if validation_errors:
                return {'error': 'Errores de validación', 'details': validation_errors}, 400

            if not update_data:
                return {'error': 'No hay campos válidos para actualizar'}, 400

            InventoryModel.update_raw(db, item_id, **update_data)
            updated_item = InventoryModel.get_by_id_raw(db, item_id)
            return {
                'message': 'Item actualizado correctamente',
                'item': dict(updated_item)
            }, 200
            
        except Exception as e:
            current_app.logger.error(f"Error al actualizar item {item_id}: {str(e)}")
            return {'error': 'Error interno al actualizar el item'}, 500

    @staticmethod
    def delete_item(item_id):
        """Elimina un item del inventario"""
        db = get_db()
        try:
            if not item_id or not isinstance(item_id, int):
                return {'error': 'ID de item inválido'}, 400

            item_to_delete = InventoryModel.get_by_id_raw(db, item_id)
            if not item_to_delete:
                return {'error': 'Item no encontrado'}, 404

            InventoryModel.delete_raw(db, item_id)
            return {
                'message': 'Item eliminado correctamente',
                'deleted_item': dict(item_to_delete)
            }, 200
            
        except Exception as e:
            current_app.logger.error(f"Error al eliminar item {item_id}: {str(e)}")
            return {'error': 'Error interno al eliminar el item'}, 500

    @staticmethod
    def search_items(item_name):
        """Busca items por nombre"""
        db = get_db()
        try:
            if not item_name or not isinstance(item_name, str):
                return {'error': 'Parámetro de búsqueda inválido'}, 400

            search_term = item_name.strip()
            if not search_term:
                return {'error': 'El término de búsqueda no puede estar vacío'}, 400

            items = InventoryModel.get_item_by_name(db, search_term)
            if not items:
                return {'message': 'No se encontraron items con ese nombre'}, 200
                
            return {
                'count': len(items),
                'results': [dict(item) for item in items]
            }, 200
            
        except Exception as e:
            current_app.logger.error(f"Error al buscar items: {str(e)}")
            return {'error': 'Error interno al realizar la búsqueda'}, 500