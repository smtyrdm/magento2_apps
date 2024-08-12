<?php
namespace Ensa\Showroom\Plugin;

use Magento\Sales\Api\Data\OrderExtensionFactory;
use Magento\Sales\Api\Data\OrderInterface;

class OrderRepositoryPlugin
{
    protected $orderExtensionFactory;

    public function __construct(OrderExtensionFactory $orderExtensionFactory)
    {
        $this->orderExtensionFactory = $orderExtensionFactory;
    }

    public function afterGet(\Magento\Sales\Api\OrderRepositoryInterface $subject, OrderInterface $result)
    {
        $extensionAttributes = $result->getExtensionAttributes();
        if ($extensionAttributes === null) {
            $extensionAttributes = $this->orderExtensionFactory->create();
        }

        $extensionAttributes->setSubCompany($result->getData('order_subcompany'));
        $result->setExtensionAttributes($extensionAttributes);

        return $result;
    }

    public function afterGetList(\Magento\Sales\Api\OrderRepositoryInterface $subject, $searchCriteria)
    {
        $orders = $searchCriteria->getItems();
        foreach ($orders as $order) {
            $extensionAttributes = $order->getExtensionAttributes();
            if ($extensionAttributes === null) {
                $extensionAttributes = $this->orderExtensionFactory->create();
            }

            $extensionAttributes->setSubCompany($order->getData('order_subcompany'));
            $order->setExtensionAttributes($extensionAttributes);
        }

        return $searchCriteria;
    }
}