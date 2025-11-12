import { useState, useCallback } from 'react'
import { ContactRecord } from '@/lib/api/contacts'

interface UseContactSelectReturn {
  isOpen: boolean
  selectedContact: ContactRecord | null
  openModal: () => void
  closeModal: () => void
  handleContactSelect: (contact: ContactRecord) => void
  resetSelection: () => void
}

export function useContactSelect(): UseContactSelectReturn {
  const [isOpen, setIsOpen] = useState(false)
  const [selectedContact, setSelectedContact] = useState<ContactRecord | null>(null)

  const openModal = useCallback(() => {
    setIsOpen(true)
  }, [])

  const closeModal = useCallback(() => {
    setIsOpen(false)
    // Limpar seleção ao fechar
    setTimeout(() => {
      setSelectedContact(null)
    }, 200) // Delay para animação do modal
  }, [])

  const handleContactSelect = useCallback((contact: ContactRecord) => {
    setSelectedContact(contact)
  }, [])

  const resetSelection = useCallback(() => {
    setSelectedContact(null)
  }, [])

  return {
    isOpen,
    selectedContact,
    openModal,
    closeModal,
    handleContactSelect,
    resetSelection
  }
}