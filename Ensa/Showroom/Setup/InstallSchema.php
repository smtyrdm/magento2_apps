<?php
namespace Ensa\Showroom\Setup;

use Magento\Framework\Setup\InstallSchemaInterface;
use Magento\Framework\Setup\ModuleContextInterface;
use Magento\Framework\Setup\SchemaSetupInterface;
use Magento\Framework\DB\Ddl\Table;

class InstallSchema implements InstallSchemaInterface
{
    public function install(SchemaSetupInterface $setup, ModuleContextInterface $context)
    {
        $installer = $setup;
        $installer->startSetup();

        if (!$installer->tableExists('sales_order')) {
            $table = $installer->getConnection()->newTable(
                $installer->getTable('sales_order')
            )
                ->addColumn(
                    'order_subcompany',
                    Table::TYPE_TEXT,
                    255,
                    ['nullable' => true, 'default' => null],
                    'Order Type'
                );
            $installer->getConnection()->createTable($table);
        } else {
            $installer->getConnection()->addColumn(
                $installer->getTable('sales_order'),
                'order_subcompany',
                [
                    'type' => Table::TYPE_TEXT,
                    'nullable' => true,
                    'default' => null,
                    'comment' => 'Order Type',
                ]
            );
        }

        $installer->endSetup();
    }
}
