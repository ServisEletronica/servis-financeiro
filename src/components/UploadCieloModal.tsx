import { useState } from 'react'
import { X, Upload, FileImage, Loader2, CheckCircle2, AlertCircle } from 'lucide-react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { showCustomToastSuccess, showCustomToastError } from '@/lib/toast'
import { RecebiveisCartaoService } from '@/services/recebiveis-cartao.service'

interface UploadCieloModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onUploadSuccess: () => void
}

export function UploadCieloModal({ open, onOpenChange, onUploadSuccess }: UploadCieloModalProps) {
  const [files, setFiles] = useState<File[]>([])
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const droppedFiles = Array.from(e.dataTransfer.files)
    handleFiles(droppedFiles)
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files)
      handleFiles(selectedFiles)
    }
  }

  const handleFiles = (newFiles: File[]) => {
    // Validar tipo de arquivo
    const validFiles = newFiles.filter(file => {
      const isImage = file.type.startsWith('image/')
      if (!isImage) {
        showCustomToastError(
          'Arquivo inválido',
          `${file.name} não é uma imagem`
        )
      }
      return isImage
    })

    // Validar tamanho (máx 10MB)
    const validSizeFiles = validFiles.filter(file => {
      const isValidSize = file.size <= 10 * 1024 * 1024
      if (!isValidSize) {
        showCustomToastError(
          'Arquivo muito grande',
          `${file.name} excede 10MB`
        )
      }
      return isValidSize
    })

    // Máximo 10 arquivos
    const totalFiles = files.length + validSizeFiles.length
    if (totalFiles > 10) {
      showCustomToastError(
        'Limite excedido',
        'Máximo de 10 arquivos por vez'
      )
      return
    }

    setFiles(prev => [...prev, ...validSizeFiles])
  }

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const handleUpload = async () => {
    if (files.length === 0) {
      showCustomToastError(
        'Nenhum arquivo selecionado',
        'Selecione pelo menos uma imagem'
      )
      return
    }

    setIsUploading(true)

    try {
      const result = await RecebiveisCartaoService.uploadCalendarios(files, 'projetado')

      // Se houver registros inseridos, consideramos sucesso (mesmo com erros parciais)
      const totalInseridos = result.data.total_registros_inseridos || 0
      const totalErros = result.data.erros?.length || 0

      if (totalInseridos > 0) {
        // Sucesso - fechar modal e limpar
        showCustomToastSuccess(
          'Upload concluído!',
          `${totalInseridos} recebíveis processados com sucesso${totalErros > 0 ? ` (${totalErros} erros)` : ''}`
        )

        // Limpar arquivos e fechar modal
        setFiles([])
        setIsUploading(false)
        onOpenChange(false)
        onUploadSuccess()
      } else {
        // Nenhum registro inserido - manter modal aberto
        showCustomToastError(
          'Erro no processamento',
          'Nenhum recebível pôde ser processado. Verifique as imagens.'
        )
        setIsUploading(false)
      }
    } catch (error: any) {
      console.error('Erro no upload:', error)
      showCustomToastError(
        'Erro ao fazer upload',
        error.response?.data?.detail || error.message || 'Erro desconhecido'
      )
      setIsUploading(false)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Upload Calendário Cielo</DialogTitle>
          <DialogDescription>
            Faça upload de imagens dos calendários de recebíveis da Cielo
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Área de Upload */}
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              isDragging
                ? 'border-primary bg-primary/5'
                : 'border-gray-300 dark:border-gray-700'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <div className="flex flex-col items-center gap-2">
              <Upload className="h-10 w-10 text-muted-foreground" />
              <div className="text-sm">
                <label htmlFor="file-upload" className="cursor-pointer text-primary hover:underline">
                  Clique para selecionar
                </label>
                <span className="text-muted-foreground"> ou arraste arquivos aqui</span>
              </div>
              <p className="text-xs text-muted-foreground">
                PNG, JPG ou JPEG (máx. 10MB cada, até 10 arquivos)
              </p>
              <input
                id="file-upload"
                type="file"
                multiple
                accept="image/*"
                onChange={handleFileInput}
                className="hidden"
              />
            </div>
          </div>

          {/* Lista de Arquivos */}
          {files.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium">Arquivos selecionados ({files.length})</h4>
              <div className="max-h-[200px] overflow-y-auto space-y-2">
                {files.map((file, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 bg-muted rounded-lg"
                  >
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      <FileImage className="h-5 w-5 text-muted-foreground flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{file.name}</p>
                        <p className="text-xs text-muted-foreground">
                          {formatFileSize(file.size)}
                        </p>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeFile(index)}
                      disabled={isUploading}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Botões de Ação */}
          <div className="flex justify-end gap-2 pt-4">
            <Button
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isUploading}
            >
              Cancelar
            </Button>
            <Button
              onClick={handleUpload}
              disabled={isUploading || files.length === 0}
            >
              {isUploading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processando...
                </>
              ) : (
                <>
                  <Upload className="mr-2 h-4 w-4" />
                  Fazer Upload
                </>
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
