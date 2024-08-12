<?php
namespace Ensa\Showroom\Plugin\Sales\Block\Adminhtml\Order\Create;

class CreateOrderPlugin
{

    public function aroundGetChildHtml(\Magento\Sales\Block\Adminhtml\Order\Create\Data $subject, callable $proceed, $id, $useCache = true)
    {
        $html = $proceed($id, $useCache);

        if ($id == 'form_account') { // <- different sections can be targeted by changing block name
            $block = $subject->getChildHtml('subcompany_block');
            $html = $html . $block;
        }

        return $html;
    }
}