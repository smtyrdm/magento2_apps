<?php
namespace Ensa\Showroom\Plugin;

use Magento\Sales\Controller\Adminhtml\Order\Create\Save as SaveAction;
use Magento\Framework\App\RequestInterface;
use Magento\Sales\Model\OrderRepository;
use Psr\Log\LoggerInterface;

class SaveOrderPlugin
{
    private $orderRepository;
    private $logger;

    public function __construct(OrderRepository $orderRepository, LoggerInterface $logger)
    {
        $this->orderRepository = $orderRepository;
        $this->logger = $logger;
    }

    public function afterExecute(SaveAction $subject, $result)
    {
        $request = $subject->getRequest();
        $customField = $request->getParam('order_subcompany_select');


        $orderId = $this->getLastOrderId();
        if ($orderId) {
            $order = $this->orderRepository->get($orderId);
            $order->setData('order_subcompany', $customField);
            $this->orderRepository->save($order);
        }

        return $result;
    }

    private function getLastOrderId()
    {
        $objectManager = \Magento\Framework\App\ObjectManager::getInstance();
        $resource = $objectManager->get('Magento\Framework\App\ResourceConnection');
        $connection = $resource->getConnection();
        $tableName = $resource->getTableName('sales_order');

        $sql = "SELECT entity_id FROM " . $tableName . " ORDER BY entity_id DESC LIMIT 1";
        $orderId = $connection->fetchOne($sql);

        return $orderId;
    }
}

