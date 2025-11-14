import { useState } from 'react'
import { Loader2 } from 'lucide-react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { showCustomToastSuccess, showCustomToastError } from '@/lib/toast'
import { RecebiveisCartaoService } from '@/services/recebiveis-cartao.service'

interface InserirRecebidoCartaoModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  data: string // Data no formato YYYY-MM-DD
  onSuccess: () => void
}

const FILIAIS = [
  { nome: 'Servis Eletrônica Ceará', estabelecimento: '1028859080' },
  { nome: 'Servis Eletrônica Maranhão', estabelecimento: '1060654811' },
  { nome: 'Secopi Serviços Piauí', estabelecimento: '1071167917' },
]

export function InserirRecebidoCartaoModal({
  open,
  onOpenChange,
  data,
  onSuccess,
}: InserirRecebidoCartaoModalProps) {
  const [filialNome, setFilialNome] = useState<string>('')
  const [valor, setValor] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)

  const formatDate = (dateStr: string) => {
    const [year, month, day] = dateStr.split('-')
    return `${day}/${month}/${year}`
  }

  const handleSubmit = async () => {
    if (!filialNome) {
      showCustomToastError(
        'Filial obrigatória',
        'Selecione uma filial'
      )
      return
    }

    if (!valor || parseFloat(valor) <= 0) {
      showCustomToastError(
        'Valor inválido',
        'Informe um valor maior que zero'
      )
      return
    }

    setIsLoading(true)

    try {
      const filial = FILIAIS.find((f) => f.nome === filialNome)
      if (!filial) {
        throw new Error('Filial não encontrada')
      }

      const mesReferencia = data.substring(0, 7) // YYYY-MM

      await RecebiveisCartaoService.inserirRecebidoManual({
        data_recebimento: data,
        valor: parseFloat(valor),
        estabelecimento: filial.estabelecimento,
        mes_referencia: mesReferencia,
      })

      showCustomToastSuccess(
        'Sucesso!',
        'Recebível registrado com sucesso'
      )

      // Limpar form e fechar
      setFilialNome('')
      setValor('')
      setIsLoading(false)
      onOpenChange(false)
      onSuccess()
    } catch (error: any) {
      console.error('Erro ao inserir recebível:', error)
      showCustomToastError(
        'Erro ao registrar',
        error.response?.data?.detail || error.message || 'Erro desconhecido'
      )
      setIsLoading(false)
    }
  }

  const handleValorChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    // Permite apenas números e vírgula/ponto
    const regex = /^[0-9]*[,.]?[0-9]*$/
    if (regex.test(value) || value === '') {
      // Substitui vírgula por ponto para cálculo
      setValor(value.replace(',', '.'))
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[450px]">
        <DialogHeader>
          <DialogTitle>Registrar Recebível de Cartão</DialogTitle>
          <DialogDescription>
            Data: {formatDate(data)}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Seleção de Filial */}
          <div className="space-y-2">
            <Label htmlFor="filial">Filial</Label>
            <Select value={filialNome} onValueChange={setFilialNome}>
              <SelectTrigger id="filial">
                <SelectValue placeholder="Selecione a filial" />
              </SelectTrigger>
              <SelectContent>
                {FILIAIS.map((filial) => (
                  <SelectItem key={filial.nome} value={filial.nome}>
                    {filial.nome}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Input de Valor */}
          <div className="space-y-2">
            <Label htmlFor="valor">Valor Recebido (R$)</Label>
            <Input
              id="valor"
              type="text"
              placeholder="0,00"
              value={valor}
              onChange={handleValorChange}
              disabled={isLoading}
            />
          </div>
        </div>

        {/* Botões de Ação */}
        <div className="flex justify-end gap-2">
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isLoading}
          >
            Cancelar
          </Button>
          <Button onClick={handleSubmit} disabled={isLoading}>
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Salvando...
              </>
            ) : (
              'Salvar'
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
