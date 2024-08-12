<?php
namespace Ensa\Showroom\Ui\Component\Listing\Column;

use \Magento\Sales\Api\OrderRepositoryInterface;
use \Magento\Framework\View\Element\UiComponent\ContextInterface;
use \Magento\Framework\View\Element\UiComponentFactory;
use \Magento\Ui\Component\Listing\Columns\Column;
use \Magento\Framework\Api\SearchCriteriaBuilder;
use \Ensa\Showroom\Block\Adminhtml\Order\Create\SubCompany;
use Magento\Framework\Pricing\PriceCurrencyInterface;

class OrderSubcompany extends Column
{
    protected $_orderRepository;
    protected $_searchCriteria;
    protected $_subCompany;

    public function __construct(
        PriceCurrencyInterface $priceCurrency,
        ContextInterface $context,
        UiComponentFactory $uiComponentFactory,
        OrderRepositoryInterface $orderRepository,
        SearchCriteriaBuilder $criteria,
        SubCompany $subCompany,
        array $components = [],
        array $data = [])
    {
        $this->_orderRepository = $orderRepository;
        $this->_searchCriteria  = $criteria;
        $this->_subCompany = $subCompany;

        $this->priceCurrency = $priceCurrency;
        parent::__construct($context, $uiComponentFactory, $components, $data);
    }

    public function prepareDataSource(array $dataSource)
    {
        if (isset($dataSource['data']['items'])) {
            foreach ($dataSource['data']['items'] as &$item) {
                $order = $this->_orderRepository->get($item["entity_id"]);
                $subCompanyValue = $order->getData("order_subcompany");

                $subCompanyData = $this->_subCompany->getSubCompanyData();
                $subCompanyLabel = '';
                foreach ($subCompanyData as $data) {
                    if ($data['value'] == $subCompanyValue and $subCompanyValue != '') {
                        $subCompanyLabel = (string)$data['label'];
                        break;
                    }
                }

                $item[$this->getData('name')] = $subCompanyLabel;
            }
        }
        return $dataSource;
    }
}
