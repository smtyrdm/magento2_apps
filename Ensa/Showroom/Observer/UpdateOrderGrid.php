<?php
namespace Ensa\Showroom\Observer;

use Magento\Framework\Event\ObserverInterface;
use Magento\Framework\Event\Observer;
use Magento\Framework\App\ResourceConnection;

class UpdateOrderGrid implements ObserverInterface
{
    protected $resource;

    public function __construct(ResourceConnection $resource)
    {
        $this->resource = $resource;
    }

    public function execute(Observer $observer)
    {
        $order = $observer->getEvent()->getOrder();
        $connection = $this->resource->getConnection();
        $tableName = $this->resource->getTableName('sales_order_grid');

        $connection->update(
            $tableName,
            ['order_subcompany' => $order->getData('order_subcompany')],
            ['entity_id = ?' => $order->getId()]
        );
    }
}
