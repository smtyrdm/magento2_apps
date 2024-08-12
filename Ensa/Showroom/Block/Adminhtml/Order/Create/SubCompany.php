<?php

namespace Ensa\Showroom\Block\Adminhtml\Order\Create;

use \Magento\Backend\Block\Template;
use \Magento\Backend\Block\Template\Context;
use \Magento\Sales\Model\Order;

class SubCompany extends Template
{
    protected $order;

    public function __construct(
        Context $context,
        Order   $order,
        array   $data = [])
    {
        $this->order = $order;
        parent::__construct($context, $data);
    }

    public function getOrderId()
    {
        $orderId = $this->getRequest()->getParam('order_id');
        return $orderId;
    }

    public function getSubcompany()
    {
        $orderId = $this->getOrderId();
        $subcompanyvalue = $this->order->load($orderId)->getData('order_subcompany');
        return $subcompanyvalue;
    }

    public function getSubcompanyLabel()
    {
        $subcompanyValue = $this->getSubcompany();
        $subCompanyData = $this->getSubCompanyData();

        foreach ($subCompanyData as $data) {
            if ($data['value'] == $subcompanyValue) {
                return (string) $data['label'];
            }
        }

        return null;
    }

    public function getSubCompanyData()
    {
        return [
            ['value' => '', 'label' => __('Seçiniz')],
            ['value' => 'ankara_fabrika', 'label' => __('Ankara Fabrika')],
            ['value' => 'shop_musteri', 'label' => __('Tischkoenig Shop')],
            ['value' => 'company_dakik_07_showroom', 'label' => __('Antalya Showroom')],
            ['value' => 'company_dakik_07_pazarlama', 'label' => __('Antalya Pazarlama')],
            ['value' => 'dmo', 'label' => __('DMO')],
            ['value' => 'trendyol', 'label' => __('Trendyol')],
        ];
    }

    public function getRemoteIp()
    {
        $orderId = $this->getOrderId();
        $remoteIp = $this->order->load($orderId)->getData('remote_ip');
        return $remoteIp;
    }
}